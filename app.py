from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# CSVデータを読み込む
def load_car_data():
    df = pd.read_csv("car_data.csv")
    return df.to_dict(orient="records")  # 辞書型リストに変換

@app.route("/", methods=["GET", "POST"])
def home():
    cars = load_car_data()

    if request.method == "POST":
        # ユーザーの選択を取得
        body_types = request.form.getlist("body_type")
        drive_types = request.form.getlist("drive_type")
        max_price = request.form.get("max_price")

        #フィルタリング処理
        filtered_cars = []
        for car in cars:
            # ボディタイプのいずれかにマッチするか
            if body_types and car["ボディタイプ"] not in body_types:
                continue
            # 駆動方式のいずれかにマッチするか
            if drive_types and car["駆動方式"] not in drive_types:
                continue
            # 上限価格の条件
            if max_price and int(car["価格(万円)"]) > int(max_price):
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
