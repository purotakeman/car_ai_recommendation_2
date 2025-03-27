from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

# CSVデータを読み込む
def load_car_data():
    df = pd.read_csv("car_data.csv")
    return df.to_dict(orient="records")  # 辞書型リストに変換

@app.route("/")
def home():
    car_list = load_car_data()
    return render_template("index.html", cars=car_list)

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
