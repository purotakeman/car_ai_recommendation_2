AI自動車診断システム

📝 プロジェクト概要
AI自動車診断システムは、自動車の知識があまりないユーザーでも、自分に最適なクルマを見つけられるウェブサービスです。ユーザーの希望（ボディタイプ、駆動方式、価格など）に基づき、AI的なロジックで車を推薦・フィルタリングします。
🎯 目的

自動車選びの複雑さを解消し、初心者でも適切な選択ができるようサポート
様々な条件や好みから個々のニーズに最適化された車両を推薦
詳細な車両情報をわかりやすく整理して提供
コストや維持費も含めた総合的な判断材料を提供

🌟 主要機能
現在実装済み

🔍 複数条件での車両検索・フィルタリング機能
🚗 車両情報の一覧表示と詳細表示
💯 ユーザーの嗜好に基づく車両推薦スコアの計算
📊 維持費シミュレーション
💾 お気に入り機能（ローカルストレージ）
🔄 検索結果の並び替え機能

開発予定

👤 ユーザーアカウント管理
📱 レスポンシブデザインの完全対応
🤖 AIによる自然言語での車両推薦
📂 詳細なユーザーレビューとコミュニティ機能
🔗 YouTubeレビュー動画の統合
🌐 SNS共有機能

🛠️ 技術スタック
バックエンド

言語: Python 3.9+
Webフレームワーク: Flask 2.3.3
データ処理: Pandas 2.0.3
Webスクレイピング: BeautifulSoup4 4.12.2, Requests 2.31.0

フロントエンド

マークアップ: HTML5, Jinja2テンプレート
スタイリング: CSS3
インタラクション: JavaScript (ECMAScript 6+)
アイコン: Font Awesome 5.15.4

データ管理

現在: CSVファイル
将来: SQLite または PostgreSQL

🚀 インストール方法
前提条件

Python 3.9以上
pip (Pythonパッケージマネージャー)
仮想環境(venv, virtualenv など)を推奨

セットアップ手順

リポジトリをクローン
bashgit clone https://github.com/yourusername/car_ai_recommendation.git
cd car_ai_recommendation

仮想環境の作成と有効化
bashpython -m venv venv
# Windowsの場合
venv\Scripts\activate
# macOS/Linuxの場合
source venv/bin/activate

依存パッケージのインストール
bashpip install -r requirements.txt

アプリケーションの起動
bashpython app.py

ブラウザで以下のURLにアクセス
http://127.0.0.1:5000/


📊 使用方法

トップページの検索フォームで条件を入力

ボディタイプ（SUV、セダン、ハッチバックなど）
駆動方式（2WD、4WDなど）
燃料タイプ（ガソリン、ハイブリッドなど）
上限価格
燃費
乗車定員


「車を診断する」ボタンをクリック
検索結果から詳細を見たい車両をクリック
詳細ページでは、スペック情報、維持費シミュレーション、レビューなどを確認可能
お気に入りボタンでお気に入りに登録可能

📂 プロジェクト構造
car_ai_recommendation/
│
├── app.py                    # メインのFlaskアプリ
├── car_data.csv              # 車データのCSVファイル
├── requirements.txt          # 依存パッケージリスト
├── README.md                 # このファイル
│
├── /templates/               # HTMLテンプレート
│   ├── index.html            # メインページ
│   ├── car_detail.html       # 車両詳細ページ
│   ├── 404.html              # 404エラーページ
│   └── 500.html              # 500エラーページ
│
├── /static/                  # 静的ファイル
│   ├── /css/                 # CSSファイル
│   ├── /js/                  # JavaScriptファイル
│   └── /images/              # 画像ファイル
│
├── /scraper/                 # スクレイピング用スクリプト
│   └── car_scraper.py        # 車両データ収集スクリプト
│
├── /data/                    # データ関連ファイル
│   └── raw_data.csv          # スクレイピング結果
│
└── /utils/                   # ユーティリティ関数
    ├── filters.py            # フィルタリング関数
    └── recommendation.py     # 推薦ロジック
🔄 データ更新方法
車両データを更新する場合は、スクレイピングスクリプトを実行します：
bash# 仮想環境を有効化
source venv/bin/activate  # または venv\Scripts\activate (Windows)

# スクレイピングスクリプトを実行
python -m scraper.car_scraper

# または既存のCSVとマージ
python -m scraper.car_scraper --merge
🤝 貢献方法

このリポジトリをフォーク
新機能のブランチを作成 (git checkout -b feature/amazing-feature)
変更をコミット (git commit -m 'Add amazing feature')
ブランチをプッシュ (git push origin feature/amazing-feature)
Pull Requestを作成

📝 ライセンス
このプロジェクトは MIT ライセンスの下で公開されています。詳細は LICENSE ファイルをご覧ください。
📧 連絡先
プロジェクト管理者: Your Name - email@example.com
プロジェクトリンク: https://github.com/yourusername/car_ai_recommendation

📸 スクリーンショット
メイン検索ページ
画像を表示
車両詳細ページ
画像を表示

このプロジェクトは個人の学習・ポートフォリオ用に作成されています。掲載されている車両情報は参考用であり、実際の購入判断には公式情報をご確認ください。