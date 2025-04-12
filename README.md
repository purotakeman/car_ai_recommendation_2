AI自動車推薦ウェブアプリ
プロジェクト概要
自動車の知識があまりないユーザーでも、自分に最適なクルマを見つけられるウェブサービスを提供することを目的としています。ユーザーの希望（ボディタイプ・駆動方式・価格など）に基づいて、AI的なロジックで車を推薦・フィルタリングします。最終的に推薦した車の情報(口コミ、モータージャーナリスト動画へ誘導など)をまとめて提供します。
主な機能

車両情報のCSV管理（メーカー・車種・価格など）
複数の条件（ボディタイプ・駆動方式・価格・燃費など）でフィルタリング可能
動的に推薦内容が変わる仕組み
ユーザーフレンドリーなインターフェース

技術スタック

開発環境: VSCode
フロントエンド: HTML, CSS, JavaScript
バックエンド: Python（Flaskフレームワーク）
データベース: CSVファイル（将来的にSQLiteなどへ拡張予定）
仮想環境管理: venv+pip
バージョン管理: GitHub
データ収集: BeautifulSoupによるWebスクレイピング（予定）

インストール方法

リポジトリをクローン
git clone https://github.com/yourusername/car_ai_recommendation.git
cd car_ai_recommendation

仮想環境を作成して有効化
python -m venv venv
# Windowsの場合
venv\Scripts\activate
# Macの場合
source venv/bin/activate

必要なパッケージをインストール
pip install -r requirements.txt

アプリケーションを実行
python app.py

ブラウザで以下のURLにアクセス
http://127.0.0.1:5000/


将来的な機能拡張予定

SQLiteやPostgreSQLなどへのデータベース移行
ユーザー登録・お気に入り機能
AIロジック（重み付け、評価スコア、将来の再販価値など）での車両レコメンド
車比較やレビュー動画統合表示

貢献方法

このリポジトリをフォーク
新しいブランチを作成 (git checkout -b feature/amazing-feature)
変更をコミット (git commit -m 'Add some amazing feature')
ブランチにプッシュ (git push origin feature/amazing-feature)
プルリクエストを作成

ライセンス
MIT