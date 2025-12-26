from flask import Flask, render_template, request, jsonify, abort, redirect, url_for
import pandas as pd
import os
import json
from datetime import datetime
from utils.youtube import get_car_videos


# 推薦スコア計算モジュールをインポート
from utils.recommendation import calculate_recommendation_scores

app = Flask(__name__)

# CSVデータを読み込む
def load_car_data():
    """
    車両データCSVファイルを読み込む
    複数のエンコーディングを試行して、文字化けを防ぐ
    """
    # ファイルパスを複数試行（新しいCSVファイル名に対応）
    csv_paths = ["data/car_data_base.csv", "data/car_data.csv", "car_data_base.csv", "car_data.csv"]
    df = None
    
    for csv_path in csv_paths:
            try:
                # UTF-8 BOM付きで読み込みを試す（Windows対応）
                df = pd.read_csv(csv_path, encoding="utf-8-sig")
                break
            except (FileNotFoundError, pd.errors.EmptyDataError):
                continue # ファイルがない、または空の場合は次のパスへ
            except UnicodeDecodeError:
                try:
                    # UTF-8で読み込みを試す
                    df = pd.read_csv(csv_path, encoding="utf-8")
                    break
                except UnicodeDecodeError:
                    try:
                        # Shift-Jisで読み込みを試す
                        df = pd.read_csv(csv_path, encoding="shift-jis")
                        break
                    except:
                        # CP932(Windows日本語)で読み込みを試す
                        df = pd.read_csv(csv_path, encoding="cp932")
                        break
                        pass
                except Exception as e:
                    print(f"予期せぬエラー: {e}")
                    continue
    
    # ファイルが見つからない場合のエラーハンドリング
    if df is None:
        print("❌ 車両データCSVファイルが見つかりません")
        print("   以下のパスを確認してください: data/car_data_base.csv")
        # 空のデータフレームを返す
        return []

    # 新しいCSV構造のカラム名（カラム名が正しく読み込まれている場合はそのまま使用）
    # カラム名にスペースが含まれる場合があるので、正規化
    df.columns = df.columns.str.strip()
    
    # 燃費カラム名の正規化（「燃費(km/L)電費(Wh/km)水素燃費(km/kg)」を「燃費(km/L)」に統一）
    if '燃費(km/L)電費(Wh/km)水素燃費(km/kg)' in df.columns:
        df.rename(columns={'燃費(km/L)電費(Wh/km)水素燃費(km/kg)': '燃費(km/L)'}, inplace=True)
    
    # 最新モデルカラム名の正規化（スペースを含む可能性）
    if '最新モデル 発表年月' in df.columns:
        df.rename(columns={'最新モデル 発表年月': '最新モデル'}, inplace=True)
    
    # 数値データの型変換（エラー処理込み）
    numeric_columns = ['自動車税(円)', '乗車定員', '排気量(cc)']
    # 排気量カラム名の確認
    if '排気量(cc)' not in df.columns and '排気量' in df.columns:
        numeric_columns.append('排気量')
    
    for col in numeric_columns:
        if col in df.columns:
            # pd.to_numeric()で数値に変換、errors='coerce'により変換できないデータはNaN（欠損値）になる
            df[col] = pd.to_numeric(df[col], errors='coerce')
            # NaN値を適切なデフォルト値で置換
            df[col] = df[col].fillna(0)
            # 整数値として扱うべきカラムを整数型にキャスト（小数点 .0 を防ぐ）
            if col in ['自動車税(円)', '乗車定員', '排気量(cc)', '排気量']:
                df[col] = df[col].astype(int)
        if '燃費(km/L)' in df.columns:
            # 欠損値を0埋めするが、文字列(範囲データ)はそのまま残す
            df['燃費(km/L)'] = df['燃費(km/L)'].fillna(0)
    
    # 不足データを適切な形式で埋める
    # fillna()で空白のデータを適切な値で埋める。データが不完全でもアプリが正常に動作するようにする
    string_columns = ['メーカー', '車種', 'ボディタイプ', '駆動方式', '燃料の種類', 'グレード・モデル', '価格帯(万円)', '先進安全装備']
    for col in string_columns:
        if col in df.columns:
            if col == 'ボディタイプ':
                df[col].fillna('不明', inplace=True)
            elif col == '駆動方式':
                df[col].fillna('不明', inplace=True)
            elif col == '燃料の種類':
                df[col].fillna('ガソリン', inplace=True)
            elif col == 'グレード・モデル':
                df[col].fillna('', inplace=True)
            elif col == '先進安全装備':
                df[col].fillna('NO', inplace=True)
            else:
                df[col].fillna('未定', inplace=True)
    
    # データ型の安全性を確保（NaN値を文字列に変換）
    for col in df.columns:
        if col not in numeric_columns:
            df[col] = df[col].astype(str).replace('nan', '未定')

            # 追加: 燃料の種類の表記漏れを統一(スペースを削除)
            # 追加: 燃料の種類の表記漏れを統一(スペースを削除)
            if col == '燃料の種類':
                df[col] = df[col].str.replace(' (', '(', regex=False)
                
                # 燃料タイプの正規化は最小限（スペースの統一のみ）にとどめる
                # index.html の値と一致させるため、スペースありを括弧直結にする
                df[col] = df[col].str.replace(' (', '(', regex=False)
                # ユーザーの要望により、レギュラー、ハイオク、HEVなどを統合せず個別に扱う
                
                # 特定の複合パターン（レギュラー(HEV)などは上のHEVルールでハイブリッドになるが、念のため）

    return df.to_dict(orient="records")  # 辞書型リストに変換

# 価格帯から最小・最大価格を抽出する関数
def parse_price_range(price_range_str):
    if not price_range_str or '~' not in str(price_range_str):
        try:
            val = float(price_range_str)
            return val, val
        except:
            return None, None
    try:
        min_p, max_p = price_range_str.split('~')
        return float(min_p), float(max_p)
    except:
        return None, None

# メインルート: 検索ページと結果表示
@app.route("/", methods=["GET", "POST"])
def home():
    """
    メインページの処理
    GET: 初期表示
    POST: 検索条件による車両フィルタリングと推薦
    """
    try:
        cars = load_car_data()
        
        # データが空の場合のエラーハンドリング
        if not cars:
            print("⚠️  車両データが読み込めませんでした")
            cars = []
        
        # 利用可能なフィルタリング条件の選択肢を取得
        filter_options = get_filter_options(cars)
    except Exception as e:
        print(f"❌ データ読み込みエラー: {e}")
        cars = []
        filter_options = {
            'body_types': [],
            'drive_types': [],
            'fuel_types': []
        }

    if request.method == "POST":
        # ユーザーの入力を取得
        body_types = request.form.getlist("body_type")
        drive_types = request.form.getlist("drive_type")
        fuel_types = request.form.getlist("fuel_type")
        

        max_price = request.form.get("max_price")
        
        # 新しい条件を追加（燃費、乗車定員）
        min_fuel_economy = request.form.get("min_fuel_economy")
        min_seats = request.form.get("min_seats")
        
        # 追加: 用途と経験レベル
        purpose = request.form.get("purpose")
        experience_level = request.form.get("experience_level")
        
        # ユーザーの嗜好情報を取得
        user_preferences = {
            'body_types': body_types,
            'drive_types': drive_types,
            'fuel_types': fuel_types,
            'max_price': max_price,
            'min_fuel_economy': min_fuel_economy,
            'min_seats': min_seats,
            'purpose': purpose,
            'experience_level': experience_level,
            'price_importance': request.form.get("price_importance", "0.5"),
            'fuel_economy_importance': request.form.get("fuel_economy_importance", "0.3"),
            'size_importance': request.form.get("size_importance", "0.2"),
            'preferred_size': request.form.get("preferred_size", "medium")
        }

        # フィルタリング処理
        filtered_cars = []
        # フィルタリング基準の作成
        filter_criteria = {
            'body_types': body_types,
            'drive_types': drive_types,
            'fuel_types': fuel_types,
            'max_price': max_price,
            'min_fuel_economy': min_fuel_economy,
            'min_seats': min_seats
        }
        

        # 共通関数でフィルタリング
        filtered_cars = filter_cars(cars, filter_criteria)
        
        # 推薦スコアを計算してソート
        if filtered_cars:
            try:
                filtered_cars = calculate_recommendation_scores(filtered_cars, user_preferences)
                
                # 車種の重複排除（同一車種の別グレードを表示しない）
                filtered_cars = deduplicate_cars(filtered_cars)
            except Exception as e:
                # 推薦計算でエラーが発生した場合のフォールバック
                print(f"推薦計算エラー: {e}")
                # 基本的なソート（価格帯の最小値順）にフォールバック
                filtered_cars.sort(key=lambda x: parse_price_range(x.get('価格帯(万円)', ''))[0] if parse_price_range(x.get('価格帯(万円)', ''))[0] is not None else 9999, reverse=False)
                # フォールバック後も重複排除を適用
                filtered_cars = deduplicate_cars(filtered_cars)
        
        # 検索条件をテンプレートに渡す（検索フォームの状態保持のため）
        search_params = {
            'body_types': body_types,
            'drive_types': drive_types,
            'fuel_types': fuel_types,
            'max_price': max_price,
            'min_fuel_economy': min_fuel_economy,
            'min_seats': min_seats,
            'purpose': purpose,
            'experience_level': experience_level
        }

        for car in filtered_cars[:10]:
            videos = get_car_videos(car.get('メーカー'), car.get('車種'), count=1)
            if videos:
                car['youtube_url'] = videos[0]['url']
                car['youtube_thumbnail'] = videos[0]['thumbnail']

        return render_template(
            "index.html", 
            cars=filtered_cars, 
            filter_options=filter_options,
            search_params=search_params,
            show_recommendation_details=True  # 推薦詳細を表示するフラグ
        )
    
    # GETリクエストの場合は初期表示（車両データは表示しない）
    # 初期表示時は車両データを渡さず、検索実行後のみ表示する
    return render_template("index.html", cars=[], filter_options=filter_options)

# 利用可能なフィルタリング条件を取得する
def get_filter_options(cars):
    """
    車両データから利用可能なフィルタリング条件を抽出
    
    Parameters:
    -----------
    cars : list
        車両データのリスト
        
    Returns:
    --------
    dict
        フィルタリング条件の辞書
    """
    # 空のデータの場合はデフォルト値を返す
    if not cars:
        return {
            'body_types': [],
            'drive_types': [],
            'fuel_types': []
        }
    
    # 各カテゴリの一意値を取得し、ソート
    body_types = sorted(list(set([
        car.get('ボディタイプ', '') for car in cars 
        if car.get('ボディタイプ') and car.get('ボディタイプ') != '不明'
    ])))
    
    drive_types = sorted(list(set([
        car.get('駆動方式', '') for car in cars 
        if car.get('駆動方式') and car.get('駆動方式') != '不明'
    ])))
    
    fuel_types = sorted(list(set([
        car.get('燃料の種類', '') for car in cars 
        if car.get('燃料の種類') and car.get('燃料の種類') != ''
    ])))
    
    return {
        'body_types': body_types,
        'drive_types': drive_types,
        'fuel_types': fuel_types
    }

# 車両詳細ページのルート
@app.route("/car/<int:car_id>")
def car_detail(car_id):
    """
    車両詳細ページの表示
    
    Parameters:
    -----------
    car_id : int
        車両ID
        
    Returns:
    --------
    レンダリングされた詳細ページまたは404エラー
    """
    cars = load_car_data()
    
    # 指定されたIDの車両を検索
    car = next((c for c in cars if int(c.get("id", 0)) == car_id), None)
    
    if car:

        # 関連する推薦車両を取得 (同じボディタイプか同じメーカーの車)
        related_cars = []
        car_body_type = car.get("ボディタイプ", "")
        car_maker = car.get("メーカー", "")
        seen_related_models = {f"{car_maker.strip().upper()}_{car.get('車種', '').strip().upper()}"}
        
        for other_car in cars:
            other_id = other_car.get("id")
            other_body_type = other_car.get("ボディタイプ", "")
            other_maker = other_car.get("メーカー", "")
            other_model = other_car.get("車種", "")
            
            # モデル識別子
            other_model_id = f"{str(other_maker).strip().upper()}_{str(other_model).strip().upper()}"
            
            # 重複（自身も含む）を除外し、ボディタイプかメーカーが一致する車両を選択
            if (other_model_id not in seen_related_models and 
                (other_body_type == car_body_type or other_maker == car_maker)):
                related_cars.append(other_car)
                seen_related_models.add(other_model_id)
                if len(related_cars) >= 5:  # 関連車両は最大5台まで
                    break
        
        # グレードバリエーションの取得（同メーカー、同車種の車）
        grade_variations = []
        for other_car in cars:
            # 自身は除外
            if other_car.get("id") == car.get("id"):
                continue
                
            # メーカーと車種が一致するものを収集
            if (other_car.get("メーカー") == car_maker and 
                other_car.get("車種") == car.get("車種")):
                grade_variations.append(other_car)
                
        # YouTube動画情報を取得 (最大5件)
        car['youtube_videos'] = get_car_videos(car_maker, car.get("車種"), count=5)
        if car['youtube_videos']:
            # 互換性のため、1番目の要素を個別のキーにも設定（他で使われている可能性があるため）
            car['youtube_url'] = car['youtube_videos'][0]['url']
            car['youtube_thumbnail'] = car['youtube_videos'][0]['thumbnail']
            car['youtube_title'] = car['youtube_videos'][0]['title']
            
        return render_template("car_detail.html", car=car, related_cars=related_cars, grade_variations=grade_variations)
    else:
        # 車両が見つからない場合は404エラー
        abort(404)

# API: 車両データをJSON形式で提供
@app.route("/api/cars")
def api_get_cars():
    """
    車両データをJSON形式で提供するAPI
    クエリパラメータによるフィルタリングに対応
    """
    cars = load_car_data()
    
    # フィルタリングパラメータを取得
    maker = request.args.get('maker')
    body_type = request.args.get('body_type')
    max_price = request.args.get('max_price')
    
    # フィルタリング適用
    if maker:
        cars = [car for car in cars if car.get('メーカー') == maker]
    if body_type:
        cars = [car for car in cars if car.get('ボディタイプ') == body_type]
    if max_price:
        try:
            max_price_value = float(max_price)
            def price_in_range(car):
                min_p, max_p = parse_price_range(car.get('価格帯(万円)', ''))
                return min_p is not None and min_p <= max_price_value
            cars = [car for car in cars if price_in_range(car)]
        except ValueError:
            # 不正な価格パラメータは無視
            pass
    
    return jsonify(cars)

@app.route("/api/cars/batch", methods=["POST"])
def api_get_cars_batch():
    """
    複数車両のIDリストを受け取り、それらの情報をJSON形式で返すAPI
    """
    data = request.get_json()
    if not data or 'ids' not in data:
        return jsonify({"error": "IDリストが指定されていません"}), 400
    
    car_ids = [int(cid) for cid in data['ids'] if str(cid).isdigit()]
    all_cars = load_car_data()
    
    # 指定されたIDに一致する車両を抽出
    selected_cars = [car for car in all_cars if int(car.get('id', 0)) in car_ids]
    
    # YouTube情報の取得（検索結果表示に合わせる）
    for car in selected_cars:
        try:
            videos = get_car_videos(car.get('メーカー'), car.get('車種'), count=1)
            if videos:
                car['youtube_url'] = videos[0]['url']
                car['youtube_thumbnail'] = videos[0]['thumbnail']
        except Exception as e:
            print(f"Batch YouTube retrieval error for {car.get('車種')}: {e}")
    
    return jsonify(selected_cars)

# API: 特定の車両情報をJSON形式で提供
@app.route("/api/cars/<int:car_id>")
def api_get_car(car_id):
    """
    特定の車両情報をJSON形式で提供するAPI
    
    Parameters:
    -----------
    car_id : int
        車両ID
        
    Returns:
    --------
    車両情報のJSONまたは404エラー
    """
    cars = load_car_data()
    car = next((c for c in cars if int(c.get("id", 0)) == car_id), None)
    
    if car:
        return jsonify(car)
    else:
        return jsonify({"error": "車両情報が見つかりません"}), 404

# API: AJAX推薦機能
@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    """
    AJAX用推薦API（ハイブリッド診断対応版）
    フロントエンドからの推薦リクエストを処理
    """
    try:
        print("API推薦リクエスト受信")
        if not request.is_json:
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        print(f"受信データ: {data}")
        
        if not data:
            print("❌ リクエストデータが空です")
            return jsonify({
                'success': False,
                'error': 'リクエストデータが空です',
                'diagnosis_type': 'unknown'
            }), 400
        
        cars = load_car_data()
        print(f"車両データ読み込み完了: {len(cars)}台")
        
        if not cars:
            print("❌ 車両データが読み込めませんでした")
            return jsonify({
                'success': False,
                'error': '車両データが読み込めませんでした',
                'diagnosis_type': 'unknown'
            }), 500
        
        # ハイブリッド診断からのデータかチェック
        is_hybrid_diagnosis = data.get('is_hybrid_diagnosis', 'user_profile' in data)
        is_detailed_search = data.get('is_detailed_search', False)
        page = int(data.get('page', 1))
        per_page = int(data.get('per_page', 12)) if is_detailed_search else 20
        
        if is_hybrid_diagnosis:
            # ハイブリッド診断用の拡張処理
            enhanced_data = enhance_hybrid_preferences(data)
            print(f"ハイブリッド診断データ受信: {data}")
        else:
            enhanced_data = data
        
        # 推薦計算または単なるフィルタリング
        try:
            # 1. フィルタリング（条件による絞り込み）
            filtered_cars = filter_cars(cars, enhanced_data)
            print(f"フィルタリング後: {len(filtered_cars)}台")
            
            if is_detailed_search:
                # 詳細検索の場合は推薦スコアを計算しない
                # 代わりにIDやメーカーなどで安定した並び順にする
                recommended_cars = sorted(filtered_cars, key=lambda x: int(x.get('id', 0)))
                # 車種の重複排除を適用
                recommended_cars = deduplicate_cars(recommended_cars)
                # スコアを明示的にクリア
                for car in recommended_cars:
                    if '推薦スコア' in car:
                        del car['推薦スコア']
                    if '推薦理由' in car:
                        del car['推薦理由']
            else:
                # スマート診断（従来またはハイブリッド）の場合はスコア計算
                recommended_cars = calculate_recommendation_scores(filtered_cars, enhanced_data)
                # 車種の重複排除
                recommended_cars = deduplicate_cars(recommended_cars)
            
            print(f"結果確定: {len(recommended_cars)}台")
        except Exception as e:
            print(f"❌ 処理エラー: {e}")
            return jsonify({
                'success': False,
                'error': f'エラーが発生しました: {str(e)}',
                'diagnosis_type': 'unknown'
            }), 500
        
        # ページネーション処理
        total_count = len(recommended_cars)
        if is_detailed_search:
            # 詳細検索は12件ずつのページネーション
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            display_cars = recommended_cars[start_idx:end_idx]
            total_pages = (total_count + per_page - 1) // per_page
            
            # デバッグ用
            print(f"Detailed Search: Page {page}, PerPage {per_page}, Total {total_count}, TotalPages {total_pages}, DisplayCars {len(display_cars)}")
        else:
            # スマート診断は上位20台
            display_cars = recommended_cars[:20]
            total_pages = 1

        response_data = {
            'success': True,
            'cars': display_cars,
            'total': total_count,
            'page': page,
            'total_pages': total_pages,
            'user_profile': enhanced_data.get('user_profile', 'general'),
            'diagnosis_type': 'hybrid' if is_hybrid_diagnosis else ('detailed' if is_detailed_search else 'simple')
        }
        
        if is_hybrid_diagnosis:
            # ハイブリッド診断の場合は詳細分析情報を追加
            response_data['analysis'] = {
                'profile_confidence': calculate_profile_confidence(enhanced_data),
                'top_factors': get_top_recommendation_factors(enhanced_data),
                'alternative_profiles': get_alternative_profiles(enhanced_data)
            }

        for car in response_data['cars']:
            videos = get_car_videos(car.get('メーカー'), car.get('車種'), count=1)
            if videos:
                car['youtube_url'] = videos[0]['url']
                car['youtube_thumbnail'] = videos[0]['thumbnail']
                
        return jsonify(response_data)
    
    except Exception as e:
        print(f"推薦API エラー: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'diagnosis_type': 'unknown'
        }), 500

def enhance_hybrid_preferences(hybrid_data):
    """
    ハイブリッド診断のデータを既存の推薦システムに適合するよう拡張
    
    Parameters:
    -----------
    hybrid_data : dict
        フロントエンドから送信されたハイブリッド診断データ
        
    Returns:
    --------
    dict
        拡張された推薦用データ
    """
    enhanced = hybrid_data.copy()
    
    # プロファイル別の詳細設定を追加
    user_profile = hybrid_data.get('user_profile', 'balance')
    
    # 燃費重要度に基づく詳細設定
    fuel_importance = float(hybrid_data.get('fuel_economy_importance', 0.6))
    if fuel_importance >= 0.8:
        enhanced['min_fuel_economy'] = enhanced.get('min_fuel_economy', '18')
        # プロファイルのデフォルトよりも厳しい燃料タイプ制限を適用
        enhanced['fuel_types'] = ['(HEV)', '(PHEV)', '電気(BEV)', '水素']
    elif fuel_importance >= 0.6:
        enhanced['min_fuel_economy'] = enhanced.get('min_fuel_economy', '15')
    
    # 安全性重要度に基づく設定
    safety_importance = float(hybrid_data.get('safety_importance', 0.6))
    if safety_importance >= 0.8:
        enhanced['min_safety_rating'] = '4'  # 新しいフィールド
    
    # デザイン重要度に基づく設定
    design_importance = float(hybrid_data.get('design_importance', 0.6))
    if design_importance >= 0.8:
        enhanced['prefer_premium_brands'] = True  # 新しいフィールド
    
    # 室内空間重要度に基づく設定
    space_importance = float(hybrid_data.get('space_importance', 0.6))
    if space_importance >= 0.8:
        if 'body_types' not in enhanced:
            enhanced['body_types'] = ['ミニバン', 'SUV', 'ワゴン']
        enhanced['preferred_size'] = 'large'
    elif space_importance <= 0.4:
        enhanced['preferred_size'] = 'small'
    
    # 維持費重要度に基づく設定
    maintenance_importance = float(hybrid_data.get('maintenance_importance', 0.6))
    if maintenance_importance >= 0.8:
        enhanced['max_tax'] = '30000'  # 新しいフィールド
        enhanced['prefer_low_maintenance'] = True  # 新しいフィールド
    

    # 【修正】5人以上乗る場合や大型希望の場合は、ハッチバックを除外する（コンパクトカーが選ばれるのを防ぐため）
    # ただし、ユーザーが明示的にハッチバックだけを指定している場合は除く
    # APIからのmin_seatsは文字列の可能性があるため安全に変換
    try:
        min_seats_val = int(enhanced.get('min_seats', 0)) if enhanced.get('min_seats') else 0
    except (ValueError, TypeError):
        min_seats_val = 0
        
    if (enhanced.get('preferred_size') == 'large' or min_seats_val >= 5):
        current_body_types = enhanced.get('body_types', [])
        if current_body_types and 'ハッチバック' in current_body_types:
            # 他のボディタイプがある場合のみ削除（ハッチバックしかない場合は残す）
            if len(current_body_types) > 1:
                enhanced['body_types'] = [bt for bt in current_body_types if bt != 'ハッチバック']
                print(f"大型希望/多人数乗車のためハッチバックを除外しました: {enhanced['body_types']}")

    return enhanced

def deduplicate_cars(cars):
    """
    同一車種（メーカー＋車種名）の重複を排除し、
    リストの中で最初に出現した（最もスコアが高い）1台のみを保持する
    """
    unique_cars = []
    seen_models = set()
    
    for car in cars:
        # メーカー名と車種名を正規化（前後スペース除去、大文字化）
        # これにより微細な表記揺れ（「TOYOTA 」と「Toyota」など）があっても正しく同一視する
        m = str(car.get('メーカー', '')).strip().upper()
        s = str(car.get('車種', '')).strip().upper()
        car_identifier = f"{m}_{s}"
        
        if car_identifier not in seen_models:
            seen_models.add(car_identifier)
            unique_cars.append(car)
            
    return unique_cars

def filter_cars(cars, criteria):
    """
    車両データを条件に基づいてフィルタリングする共通関数
    
    Parameters:
    -----------
    cars : list
        フィルタリング対象の車両リスト
    criteria : dict
        フィルタリング条件（body_types, fuel_types, max_price, min_fuel_economy, min_seatsなど）
        
    Returns:
    --------
    list
        フィルタリングされた車両リスト
    """
    filtered = []
    
    # 条件の抽出（単数形・複数形の両方のキーに対応）
    body_types = criteria.get('body_types') or criteria.get('body_type')
    drive_types = criteria.get('drive_types') or criteria.get('drive_type')
    fuel_types = criteria.get('fuel_types') or criteria.get('fuel_type')
    max_price = criteria.get('max_price')
    min_fuel_economy = criteria.get('min_fuel_economy')
    min_seats = criteria.get('min_seats')
    
    # リスト形式でない場合はリストに変換（文字列が1つだけ送られてきた場合などの対策）
    def ensure_list(val):
        if val is None: return []
        if isinstance(val, list): return val
        return [str(val)]

    body_types = ensure_list(body_types)
    drive_types = ensure_list(drive_types)
    fuel_types = ensure_list(fuel_types)

    for car in cars:
        # ボディタイプのフィルタリング
        if body_types and car.get("ボディタイプ") not in body_types:
            continue

        # 駆動方式のフィルタリング
        if drive_types:
            car_drive = car.get("駆動方式", "")
            match = False
            for dt in drive_types:
                if dt == car_drive or dt in car_drive:
                    match = True
                    break
            if not match:
                continue

        # 燃料タイプのフィルタリング
        if fuel_types:
            car_fuel = car.get("燃料の種類", "")
            # リストのいずれかに一致するか確認（部分一致も許容して堅牢にする）
            match = False
            for ft in fuel_types:
                if ft == car_fuel or ft in car_fuel:
                    match = True
                    break
            if not match:
                continue

        # 上限価格のフィルタリング
        if max_price:
            try:
                min_p, max_p = parse_price_range(car.get('価格帯(万円)', ''))
                max_price_val = float(max_price)
                
                # 価格単位の補正（データが円単位で、入力が万円単位の場合）
                # 10000以上なら円単位とみなして万円に変換
                if min_p > 10000:
                    min_p = min_p / 10000
                    
                if min_p is not None and min_p > max_price_val:
                    continue
            except (ValueError, TypeError):
                pass
        
        # 燃費のフィルタリング
        if min_fuel_economy:
            try:
                if car.get("燃費(km/L)"):
                    car_fuel = float(car["燃費(km/L)"])
                    min_fuel_val = float(min_fuel_economy)
                    if car_fuel < min_fuel_val:
                        continue
            except (ValueError, TypeError):
                pass
        
        # 乗車定員のフィルタリング
        if min_seats:
            try:
                # 文字列型で来る可能性も考慮
                min_seats_val = int(min_seats)
                
                # 車両データの乗車定員を取得（数値が含まれているか確認）
                car_seats_val = 0
                if car.get("乗車定員"):
                    import re
                    seats_str = str(car["乗車定員"])
                    # "5名" "5" "7~8人" などの形式に対応
                    seats_match = re.search(r'(\d+)', seats_str)
                    if seats_match:
                        car_seats_val = int(seats_match.group(1))
                
                # 定員が不明(0)の場合は除外しない（安全側）か、厳密にするか
                # ここではデータがある場合のみチェックする
                if car_seats_val > 0 and car_seats_val < min_seats_val:
                    continue
                    
            except (ValueError, TypeError):
                pass
        
        filtered.append(car)
        
    return filtered

def calculate_profile_confidence(preferences):
    """
    プロファイル判定の信頼度を計算
    
    Parameters:
    -----------
    preferences : dict
        ユーザーの嗜好データ
        
    Returns:
    --------
    float
        信頼度（0.0-1.0）
    """
    # 重要度の分散を計算して信頼度とする
    importance_values = [
        float(preferences.get('fuel_economy_importance', 0.6)),
        float(preferences.get('safety_importance', 0.6)),
        float(preferences.get('design_importance', 0.6)),
        float(preferences.get('space_importance', 0.6)),
        float(preferences.get('maintenance_importance', 0.6))
    ]
    
    # 分散が大きいほど（回答にメリハリがあるほど）信頼度が高い
    import statistics
    variance = statistics.variance(importance_values)
    confidence = min(1.0, variance * 2)  # 正規化
    
    return round(confidence, 2)

def get_top_recommendation_factors(preferences):
    """
    推薦の主要な決定要因を取得
    
    Parameters:
    -----------
    preferences : dict
        ユーザーの嗜好データ
        
    Returns:
    --------
    list
        主要要因のリスト
    """
    factors = []
    
    # 各重要度をチェックして上位要因を特定
    importance_map = {
        'fuel_economy_importance': ('燃費性能', 'ガソリン代を抑えられる経済的な車'),
        'safety_importance': ('安全性', '家族を守る充実した安全装備'),
        'design_importance': ('デザイン', 'スタイリッシュで魅力的な外観'),
        'space_importance': ('室内空間', 'ゆったりとした快適な車内空間'),
        'maintenance_importance': ('維持費', '税金やメンテナンス費用が安い')
    }
    
    # 重要度の高い順にソート
    sorted_factors = sorted(
        importance_map.items(),
        key=lambda x: float(preferences.get(x[0], 0.6)),
        reverse=True
    )
    
    # 上位3つまでを取得（重要度0.6以上のもの）
    for key, (name, description) in sorted_factors[:3]:
        importance = float(preferences.get(key, 0.6))
        if importance >= 0.6:
            factors.append({
                'name': name,
                'description': description,
                'importance': importance
            })
    
    return factors

def get_alternative_profiles(preferences):
    """
    代替プロファイルの提案を取得
    
    Parameters:
    -----------
    preferences : dict
        ユーザーの嗜好データ
        
    Returns:
    --------
    list
        代替プロファイルのリスト
    """
    current_profile = preferences.get('user_profile', 'balance')
    
    # プロファイル特徴の定義
    profile_characteristics = {
        'family': ['安全性重視', '室内空間重視', '実用性重視'],
        'commuter': ['燃費重視', '維持費重視', 'コンパクト'],
        'luxury': ['デザイン重視', '品質重視', 'ブランド重視'],
        'eco': ['環境性能重視', '燃費最優先', '先進技術'],
        'balance': ['バランス重視', '汎用性', '無難な選択']
    }
    
    alternatives = []
    for profile, characteristics in profile_characteristics.items():
        if profile != current_profile:
            alternatives.append({
                'profile': profile,
                'name': get_profile_display_name(profile),
                'characteristics': characteristics
            })
    
    # 現在の嗜好に近い順にソート（簡易実装）
    return alternatives[:2]  # 上位2つまで

def get_profile_display_name(profile):
    """
    プロファイルの表示名を取得
    """
    names = {
        'family': 'ファミリー重視タイプ',
        'commuter': '通勤・実用重視タイプ',
        'luxury': '高級・品質重視タイプ',
        'eco': 'エコ・環境重視タイプ',
        'balance': 'バランス重視タイプ'
    }
    return names.get(profile, 'バランス重視タイプ')

# お気に入り機能のルート（将来的な実装）
@app.route("/favorites")
def favorites():
    """
    お気に入り機能のページ
    現在は基本的なテンプレート表示のみ
    実際の実装ではユーザー認証やセッション管理が必要
    """
    return render_template("favorites.html")



# エラーハンドリング
@app.errorhandler(404)
def page_not_found(e):
    """404エラーの処理"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """500エラーの処理"""
    return render_template('500.html'), 500

# テンプレートで使用するグローバル関数の設定
@app.context_processor
def utility_processor():
    """
    テンプレート内で使用できるユーティリティ関数を定義
    """
    def format_currency(value):
        """
        数値を通貨形式でフォーマット
        10000以上の値は万円単位に変換して表示
        """
        try:
            if pd.isna(value) or value == '' or value is None:
                return "0"

            # 文字列にして処理
            str_val = str(value).strip()
            
            # 正規化：全角チルダ、波ダッシュを半角チルダに
            str_val = str_val.replace('～', '~').replace('〜', '~')

            def format_single_value(v_str):
                try:
                    # カンマ、単位などを除去して数値変換
                    clean_str = str(v_str).replace(',', '').replace('万円', '').replace('円', '').strip()
                    if not clean_str:
                        return v_str
                        
                    v = float(clean_str)
                    
                    # 100,000以上の値は円単位とみなして万円に変換（価格表示用）
                    # ただし、コンテキストによっては円単位のままにしたい場合があるが、
                    # 現在のデータ構造では価格（万円）フィールドに円が入っているケースに対応
                    if v >= 100000:
                        v = v / 10000
                        
                    # 整数なら整数表示、小数なら小数点1桁まで
                    if v.is_integer():
                        return f"{int(v):,}"
                    else:
                        return f"{v:,.1f}"
                except (ValueError, TypeError):
                    return v_str

            # 「~」が含まれている場合は分割して処理
            if '~' in str_val:
                parts = str_val.split('~')
                formatted_parts = [format_single_value(p) for p in parts]
                return '～'.join(formatted_parts) 

            return format_single_value(str_val)
            
        except (ValueError, TypeError):
            return str(value) if value is not None else "0"
            
    def format_date():
        """
        現在の日付をフォーマット
        """
        return datetime.now().strftime('%Y年%m月%d日')
    
    def safe_get(dictionary, key, default=""):
        """
        辞書から安全に値を取得
        """
        if isinstance(dictionary, dict):
            return dictionary.get(key, default)
        return default
        
    return dict(
        format_currency=format_currency, 
        format_date=format_date,
        safe_get=safe_get
    )

# 開発モードで実行
if __name__ == "__main__":
    # 必要なディレクトリの作成
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # デバッグ情報の表示
    
    # 本番環境ではデバッグモードを無効化
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))