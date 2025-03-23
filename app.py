from flask import Flask, render_template

app = Flask(__name__)

# ルートURL（ホームページ）
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)




##app = Flask(__name__)でFlaskアプリを作成する
##@app.route('/')ルートURL/にアクセスしたときの処理を定義
##render_template('index.html')でtemplates/index.htmlを表示
##app.run(debug=True)でアプリを起動（デバッグモードON）
