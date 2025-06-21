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

    # カラム名を手動で設定
    df.columns = [
        'id', 'メーカー', '車種', 'ボディタイプ', '駆動方式', '価格(万円)', 
        '排気量', '年式', 'モデル', '安全評価', '燃費(km/L)', '燃料の種類', 
        '自動車税(円)', '乗車定員', '中古相場(万円)', 'サイズ(mm)'
    ]
    
    # 数値データの型変換
    for col in ['価格(万円)', '燃費(km/L)', '自動車税(円)', '乗車定員']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce') #pd.to_numeric()で数値に変換 #errors='coerce'により、変換できないデータはNaN（欠損値）になる
    
    # 不足データを適切な形式で埋める
    df['ボディタイプ'].fillna('不明', inplace=True)
    df['駆動方式'].fillna('不明', inplace=True)
    df['燃料の種類'].fillna('ガソリン', inplace=True)
          #fillna()で空白のデータを適切な値で埋める #データが不完全でもアプリが正常に動作するようにする

    return df.to_dict(orient="records")  # 辞書型リストに変換

# メインルート: 検索ページと結果表示
@app.route("/", methods=["GET", "POST"])
def home():
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
        
        # ユーザーの嗜好情報を取得
        user_preferences = {
            'price_importance': request.form.get("price_importance", "0.5"),
            'fuel_economy_importance': request.form.get("fuel_economy_importance", "0.3"),
            'size_importance': request.form.get("size_importance", "0.2"),
            'preferred_size': request.form.get("preferred_size", "medium")
        }

        # フィルタリング処理
        filtered_cars = []
        for car in cars:
            # ボディタイプのフィルタリング
            if body_types and car["ボディタイプ"] not in body_types:
                continue

            # 駆動方式のフィルタリング
            if drive_types and car["駆動方式"] not in drive_types:
                continue

            # 燃料タイプのフィルタリング
            if fuel_types and car["燃料の種類"] not in fuel_types:
                continue

            # 上限価格のフィルタリング
            if max_price and max_price.strip() and float(car["価格(万円)"]) > float(max_price):
                continue
            
            # 燃費のフィルタリング（新規追加）
            if min_fuel_economy and min_fuel_economy.strip() and car.get("燃費(km/L)"):
                try:
                    if float(car["燃費(km/L)"]) < float(min_fuel_economy):
                        continue
                except (ValueError, TypeError):
                    # 値が変換できない場合は条件を無視
                    pass
            
            # 乗車定員のフィルタリング（新規追加）
            if min_seats and min_seats.strip() and car.get("乗車定員"):
                try:
                    if int(float(car["乗車定員"])) < int(min_seats):
                        continue
                except (ValueError, TypeError):
                    # 値が変換できない場合は条件を無視
                    pass
            
            filtered_cars.append(car)
        
        # 推薦スコアを計算してソート
        if filtered_cars:
            filtered_cars = calculate_recommendation_scores(filtered_cars, user_preferences)
        
        # 検索条件をセッションに保存 (実際のセッション管理は将来実装)
        search_params = {
            'body_types': body_types,
            'drive_types': drive_types,
            'fuel_types': fuel_types,
            'max_price': max_price,
            'min_fuel_economy': min_fuel_economy,
            'min_seats': min_seats
        }

        return render_template(
            "index.html", 
            cars=filtered_cars, 
            filter_options=filter_options,
            search_params=search_params
        )
    
    # GETリクエストの場合はデフォルトのソート（メーカー順など）
    cars.sort(key=lambda x: (x["メーカー"], x["車種"]))
    return render_template("index.html", cars=cars, filter_options=filter_options)

# 利用可能なフィルタリング条件を取得する
def get_filter_options(cars):
    body_types = sorted(list(set([car.get('ボディタイプ', '') for car in cars if car.get('ボディタイプ')])))
    drive_types = sorted(list(set([car.get('駆動方式', '') for car in cars if car.get('駆動方式')])))
    fuel_types = sorted(list(set([car.get('燃料の種類', '') for car in cars if car.get('燃料の種類')])))
    
    return {
        'body_types': body_types,
        'drive_types': drive_types,
        'fuel_types': fuel_types
    }

# 車両詳細ページのルート
@app.route("/car/<int:car_id>")
def car_detail(car_id):
    cars = load_car_data()
    car = next((c for c in cars if int(c["id"]) == car_id), None)
    
    if car:
        # 関連する推薦車両を取得 (同じボディタイプか同じメーカーの車)
        related_cars = []
        for other_car in cars:
            if other_car["id"] != car["id"] and (
                other_car["ボディタイプ"] == car["ボディタイプ"] or 
                other_car["メーカー"] == car["メーカー"]
            ):
                related_cars.append(other_car)
                if len(related_cars) >= 3:  # 関連車両は最大3台まで
                    break
        
        return render_template("car_detail.html", car=car, related_cars=related_cars)
    else:
        return "車両情報が見つかりません", 404

# API: 車両データをJSON形式で提供
@app.route("/api/cars")
def api_get_cars():
    cars = load_car_data()
    
    # フィルタリングパラメータを取得
    maker = request.args.get('maker')
    body_type = request.args.get('body_type')
    max_price = request.args.get('max_price')
    
    # フィルタリング適用
    if maker:
        cars = [car for car in cars if car['メーカー'] == maker]
    if body_type:
        cars = [car for car in cars if car['ボディタイプ'] == body_type]
    if max_price:
        try:
            max_price_value = float(max_price)
            cars = [car for car in cars if float(car['価格(万円)']) <= max_price_value]
        except ValueError:
            pass
    
    return jsonify(cars)

# API: 特定の車両情報をJSON形式で提供
@app.route("/api/cars/<int:car_id>")
def api_get_car(car_id):
    cars = load_car_data()
    car = next((c for c in cars if int(c["id"]) == car_id), None)
    
    if car:
        return jsonify(car)
    else:
        return jsonify({"error": "車両情報が見つかりません"}), 404

# お気に入り機能のルート（将来的な実装）
@app.route("/favorites")
def favorites():
    # 実際の実装ではユーザー認証やセッション管理が必要
    return render_template("favorites.html")

# エラーハンドリング
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# テンプレートで使用するグローバル関数の設定
@app.context_processor
def utility_processor():
    def format_currency(value):
        try:
            return f"{int(float(value)):,}"
        except (ValueError, TypeError):
            return value
            
    def format_date():
        return datetime.now().strftime('%Y年%m月%d日')
        
    return dict(format_currency=format_currency, format_date=format_date)

# 開発モードで実行
if __name__ == "__main__":
    # 必要なディレクトリの作成
    os.makedirs('static/images', exist_ok=True)
    
    # デバッグモードで実行
    app.run(debug=True)