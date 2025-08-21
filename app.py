from flask import Flask, render_template, request, jsonify, abort, redirect, url_for
import pandas as pd
import os
import json
from datetime import datetime

# 推薦スコア計算モジュールをインポート
from utils.recommendation import calculate_recommendation_scores

app = Flask(__name__)

# CSVデータを読み込む
def load_car_data():
    """
    車両データCSVファイルを読み込む
    複数のエンコーディングを試行して、文字化けを防ぐ
    """
    try:
        # UTF-8 BOM付きで読み込みを試す（Windows対応）
        df = pd.read_csv("car_data.csv", encoding="utf-8-sig")
    except:
        try:
            # UTF-8で読み込みを試す
            df = pd.read_csv("car_data.csv", encoding="utf-8")
        except:
            try:
                # Shift-Jisで読み込みを試す
                df = pd.read_csv("car_data.csv", encoding="shift-jis")
            except:
                # CP932(Windows日本語)で読み込みを試す
                df = pd.read_csv("car_data.csv", encoding="cp932")

    # カラム名を手動で設定（CSVのヘッダーが正しく読み込まれない場合の対策）
    expected_columns = [
        'id', 'メーカー', '車種', 'ボディタイプ', '駆動方式', '価格(万円)', 
        '排気量', '年式', 'モデル', '安全評価', '燃費(km/L)', '燃料の種類', 
        '自動車税(円)', '乗車定員', '中古相場(万円)', 'サイズ(mm)'
    ]
    
    # カラム数が一致する場合のみカラム名を設定
    if len(df.columns) == len(expected_columns):
        df.columns = expected_columns
    
    # 数値データの型変換（エラー処理込み）
    numeric_columns = ['価格(万円)', '燃費(km/L)', '自動車税(円)', '乗車定員', '排気量', '年式', '安全評価']
    for col in numeric_columns:
        if col in df.columns:
            # pd.to_numeric()で数値に変換、errors='coerce'により変換できないデータはNaN（欠損値）になる
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 不足データを適切な形式で埋める
    # fillna()で空白のデータを適切な値で埋める。データが不完全でもアプリが正常に動作するようにする
    if 'ボディタイプ' in df.columns:
        df['ボディタイプ'].fillna('不明', inplace=True)
    if '駆動方式' in df.columns:
        df['駆動方式'].fillna('不明', inplace=True)
    if '燃料の種類' in df.columns:
        df['燃料の種類'].fillna('ガソリン', inplace=True)
    if 'モデル' in df.columns:
        df['モデル'].fillna('', inplace=True)

    return df.to_dict(orient="records")  # 辞書型リストに変換

# メインルート: 検索ページと結果表示
@app.route("/", methods=["GET", "POST"])
def home():
    """
    メインページの処理
    GET: 初期表示
    POST: 検索条件による車両フィルタリングと推薦
    """
    cars = load_car_data()
    
    # 利用可能なフィルタリング条件の選択肢を取得
    filter_options = get_filter_options(cars)

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
        for car in cars:
            # ボディタイプのフィルタリング
            if body_types and car.get("ボディタイプ") not in body_types:
                continue

            # 駆動方式のフィルタリング
            if drive_types and car.get("駆動方式") not in drive_types:
                continue

            # 燃料タイプのフィルタリング
            if fuel_types and car.get("燃料の種類") not in fuel_types:
                continue

            # 上限価格のフィルタリング
            if max_price and max_price.strip():
                try:
                    car_price = float(car.get("価格(万円)", 0))
                    max_price_val = float(max_price)
                    if car_price > max_price_val:
                        continue
                except (ValueError, TypeError):
                    # 価格データが不正な場合はスキップしない
                    pass
            
            # 燃費のフィルタリング（新規追加）
            if min_fuel_economy and min_fuel_economy.strip() and car.get("燃費(km/L)"):
                try:
                    car_fuel = float(car["燃費(km/L)"])
                    min_fuel_val = float(min_fuel_economy)
                    if car_fuel < min_fuel_val:
                        continue
                except (ValueError, TypeError):
                    # 値が変換できない場合は条件を無視
                    pass
            
            # 乗車定員のフィルタリング（新規追加）
            if min_seats and min_seats.strip() and car.get("乗車定員"):
                try:
                    car_seats = int(float(car["乗車定員"]))
                    min_seats_val = int(min_seats)
                    if car_seats < min_seats_val:
                        continue
                except (ValueError, TypeError):
                    # 値が変換できない場合は条件を無視
                    pass
            
            filtered_cars.append(car)
        
        # 推薦スコアを計算してソート
        if filtered_cars:
            try:
                filtered_cars = calculate_recommendation_scores(filtered_cars, user_preferences)
            except Exception as e:
                # 推薦計算でエラーが発生した場合のフォールバック
                print(f"推薦計算エラー: {e}")
                # 基本的なソート（価格順）にフォールバック
                filtered_cars.sort(key=lambda x: float(x.get('価格(万円)', 999)), reverse=False)
        
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

        return render_template(
            "index.html", 
            cars=filtered_cars, 
            filter_options=filter_options,
            search_params=search_params,
            show_recommendation_details=True  # 推薦詳細を表示するフラグ
        )
    
    # GETリクエストの場合はデフォルトのソート（メーカー順など）
    cars.sort(key=lambda x: (x.get("メーカー", ""), x.get("車種", "")))
    return render_template("index.html", cars=cars, filter_options=filter_options)

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
        
        for other_car in cars:
            other_id = other_car.get("id")
            other_body_type = other_car.get("ボディタイプ", "")
            other_maker = other_car.get("メーカー", "")
            
            # 同じ車両は除外し、ボディタイプかメーカーが一致する車両を関連車両とする
            if (other_id != car.get("id") and 
                (other_body_type == car_body_type or other_maker == car_maker)):
                related_cars.append(other_car)
                if len(related_cars) >= 3:  # 関連車両は最大3台まで
                    break
        
        return render_template("car_detail.html", car=car, related_cars=related_cars)
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
            cars = [car for car in cars if float(car.get('価格(万円)', 0)) <= max_price_value]
        except ValueError:
            # 不正な価格パラメータは無視
            pass
    
    return jsonify(cars)

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
        data = request.get_json()
        cars = load_car_data()
        
        # ハイブリッド診断からのデータかチェック
        is_hybrid_diagnosis = 'user_profile' in data
        
        if is_hybrid_diagnosis:
            # ハイブリッド診断用の拡張処理
            enhanced_data = enhance_hybrid_preferences(data)
            print(f"ハイブリッド診断データ受信: {data}")
            print(f"拡張後のデータ: {enhanced_data}")
        else:
            # 従来の簡単診断データ
            enhanced_data = data
        
        # 推薦計算
        recommended_cars = calculate_recommendation_scores(cars, enhanced_data)
        
        # ハイブリッド診断の場合は追加情報を含める
        response_data = {
            'success': True,
            'cars': recommended_cars[:10],  # 上位10台
            'total': len(recommended_cars),
            'user_profile': enhanced_data.get('user_profile', 'general'),
            'diagnosis_type': 'hybrid' if is_hybrid_diagnosis else 'simple'
        }
        
        if is_hybrid_diagnosis:
            # ハイブリッド診断の場合は詳細分析情報を追加
            response_data['analysis'] = {
                'profile_confidence': calculate_profile_confidence(enhanced_data),
                'top_factors': get_top_recommendation_factors(enhanced_data),
                'alternative_profiles': get_alternative_profiles(enhanced_data)
            }
        
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
        if 'fuel_types' not in enhanced:
            enhanced['fuel_types'] = ['ハイブリッド', 'EV']
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
            enhanced['body_types'] = ['ミニバン', 'SUV']
        enhanced['preferred_size'] = 'large'
    elif space_importance <= 0.4:
        enhanced['preferred_size'] = 'small'
    
    # 維持費重要度に基づく設定
    maintenance_importance = float(hybrid_data.get('maintenance_importance', 0.6))
    if maintenance_importance >= 0.8:
        enhanced['max_tax'] = '30000'  # 新しいフィールド
        enhanced['prefer_low_maintenance'] = True  # 新しいフィールド
    
    return enhanced

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

# 車両比較機能のルート
@app.route("/compare")
def compare_cars():
    """
    車両比較ページ
    複数の車両を並べて比較表示
    """
    car_ids = request.args.getlist('ids')
    if not car_ids:
        return redirect(url_for('home'))
    
    cars = load_car_data()
    selected_cars = [car for car in cars if str(car.get('id', '')) in car_ids]
    
    if not selected_cars:
        return redirect(url_for('home'))
    
    # 比較用データの準備
    comparison_data = prepare_comparison_data(selected_cars)
    
    return render_template("car_compare.html", 
                         cars=selected_cars,
                         comparison_data=comparison_data)

def prepare_comparison_data(cars):
    """
    車両比較用のデータを準備
    
    Parameters:
    -----------
    cars : list
        比較対象の車両リスト
        
    Returns:
    --------
    dict
        比較表示用のデータ
    """
    comparison_data = {
        'categories': [
            '価格', '燃費', '安全性', '維持費', 'ブランド',
            '環境性能', '乗車定員', '荷室容量'
        ],
        'charts_data': {}
    }
    
    # 各車両のレーダーチャート用データを準備
    for car in cars:
        car_name = f"{car.get('メーカー', '')} {car.get('車種', '')}"
        
        # 詳細スコアがある場合は使用、なければ簡易計算
        if 'detailed_scores' in car:
            scores = car['detailed_scores']
        else:
            # 簡易スコア計算
            price = float(car.get('価格(万円)', 300))
            fuel_economy = float(car.get('燃費(km/L)', 15))
            safety = float(car.get('安全評価', 3))
            
            scores = {
                'price': min(100, int(500 / max(1, price) * 100)),  # 安いほど高スコア
                'fuel_economy': min(100, int(fuel_economy * 4)),     # 燃費の4倍をスコア
                'safety': int(safety * 20),                         # 5段階を100点満点に
                'maintenance': 70,  # デフォルト値
                'brand': 80,       # デフォルト値
                'environmental': 60  # デフォルト値
            }
        
        comparison_data['charts_data'][car_name] = [
            scores.get('price', 50),
            scores.get('fuel_economy', 50),
            scores.get('safety', 60),
            scores.get('maintenance', 70),
            scores.get('brand', 80),
            scores.get('environmental', 60),
            int(car.get('乗車定員', 5)) * 20,  # 5人乗りを100点とする
            80  # 荷室容量（仮想値）
        ]
    
    return comparison_data

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
        """
        try:
            if pd.isna(value) or value == '' or value is None:
                return "0"
            return f"{int(float(value)):,}"
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
    print("="*50)
    print("🚗 AI自動車推薦システム 起動中...")
    print("="*50)
    
    # CSVファイルの存在確認
    if os.path.exists('car_data.csv'):
        try:
            cars = load_car_data()
            print(f"✅ 車両データ読み込み成功: {len(cars)}台")
            
            # データ品質チェック
            makers = set(car.get('メーカー', '') for car in cars if car.get('メーカー'))
            body_types = set(car.get('ボディタイプ', '') for car in cars if car.get('ボディタイプ'))
            
            print(f"📊 メーカー数: {len(makers)}")
            print(f"📊 ボディタイプ数: {len(body_types)}")
            
        except Exception as e:
            print(f"❌ データ読み込みエラー: {e}")
    else:
        print("⚠️  car_data.csv が見つかりません")
        print("   以下のコマンドでサンプルデータを作成してください:")
        print("   python -c \"import pandas as pd; pd.DataFrame([{'id':1,'メーカー':'トヨタ','車種':'プリウス','ボディタイプ':'ハッチバック','駆動方式':'2WD','価格(万円)':250,'燃費(km/L)':32.6,'燃料の種類':'ハイブリッド','自動車税(円)':34500,'乗車定員':5}]).to_csv('car_data.csv', index=False, encoding='utf-8-sig')\"")
    
    print("="*50)
    print("🌐 アクセス先: http://localhost:5000/")
    print("🛑 停止方法: Ctrl+C")
    print("="*50)
    
    # デバッグモードで実行
    app.run(debug=True)