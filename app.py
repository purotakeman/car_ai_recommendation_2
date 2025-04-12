from flask import Flask, render_template, request
import pandas as pd
import os

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

    # 念のため、カラム名を手動で設定
    df.columns = [
        'id', 'メーカー', '車種', 'ボディタイプ', '駆動方式', '価格(万円)', 
        '排気量', '年式', 'モデル', '安全評価', '燃費(km/L)', '燃料の種類', 
        '自動車税(円)', '乗車定員', '中古相場(万円)', 'サイズ(mm)'
    ]

    return df.to_dict(orient="records")  # 辞書型リストに変換

@app.route("/", methods=["GET", "POST"])
def home():
    cars = load_car_data()

    if request.method == "POST":
        # ユーザーの選択を取得
        body_types = request.form.getlist("body_type")
        drive_types = request.form.getlist("drive_type")
        fuel_types = request.form.getlist("fuel_type")
        max_price = request.form.get("max_price")

        #フィルタリング処理
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
            if max_price and max_price.strip() and int(float(car["価格(万円)"])) > int(max_price):
                continue
            
            filtered_cars.append(car)

        return render_template("index.html", cars=filtered_cars)
    
    return render_template("index.html", cars=cars)

if __name__ == "__main__":
    app.run(debug=True)




# from googleapiclient.discovery import build

# API_KEY = "YOUR_YOUTUBE_API_KEY"
# youtube = build("youtube", "v3", developerKey=API_KEY)

# def get_youtube_videos(query):
    # request = youtube.search().list(
        # part="snippet",
        # q=query,
        # type="video",
        # maxResults=3
    # )
    # response = request.execute()
    # return response['items']






##app = Flask(__name__)でFlaskアプリを作成する
##@app.route('/')ルートURL/にアクセスしたときの処理を定義
##render_template('index.html')でtemplates/index.htmlを表示
##app.run(debug=True)でアプリを起動（デバッグモードON）
