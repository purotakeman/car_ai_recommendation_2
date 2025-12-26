# AI自動車診断システム

## 📝 プロジェクト概要
AI自動車診断システムは、自動車の知識がないユーザーでも、簡単に最適なクルマを見つけられるWebアプリケーションです。ユーザーの希望（ボディタイプ、駆動方式、価格など）に基づき、高度なロジックで車両を推薦・フィルタリングします。

## 🎯 目的
- 自動車選びの複雑さを解消し、初心者でも適切な選択ができるようサポート
- 様々な条件や好みから個々のニーズに最適化された車両を推薦
- 詳細な車両情報をわかりやすく整理して提供
- 検索された車両をモータージャーナリストによる実際のレビューと比較して、より信頼性のある推薦を行う


## 🌟 主要機能

### 現在実装済み
- 🔍 **ハイブリッド診断（AI推薦）**: 質問形式でユーザーのプロファイルを判定し、最適な5台を推薦。
- 🔎 **詳細検索**: ボディタイプ、燃費、価格、駆動方式など1200件以上のデータから詳細な絞り込みが可能。
- 💯 **推薦スコア計算**: 嗜好に合わせて「安全性」「燃費」「価格」などの項目を独自にスコアリング。
- 📑 **スマートページネーション**: 大量の検索結果を1ページ12件ずつ、デザインを損なわず高速に表示。
- 💾 **お気に入り機能**: `localStorage` を使用。3x3のグリッド形式（最大9件）で詳細な車両カードを保存可能。
- 🔗 **YouTube レビュー連携**: 各車両の動画サムネイルを表示。動画がない場合は専用のプレースホルダーを表示。
- 🛡️ **セキュアな設計**: APIキーは `.env` で管理。機密情報の Git 漏洩を防ぐ [.gitignore](cci:7://file:///c:/car_ai_recommendation/car_ai_recommendation_2/.gitignore:0:0-0:0) を適用済み。
- 📱 **フルレスポンシブ**: PCからスマホまで、どのデバイスでも直感的に操作可能なモダンUI。



## 🛠️ 技術スタック

### バックエンド
- **言語**: Python 3.9+
- **Webフレームワーク**: Flask 2.3.3
- **データ処理**: Pandas 2.0.3
- **python-dotenv**: 環境変数の安全な読み込み

### フロントエンド
- **マークアップ**: HTML5
- **スタイリング**: CSS3（レスポンシブデザイン）
- **インタラクション**: JavaScript (ES6+)
- **アイコン**: Font Awesome 5.15.4

### 外部サービス
- **YouTube Data API v3**: 車両レビュー動画情報の動的取得。

### データ管理
- **現在**: CSVファイル
- **将来**: SQLite または PostgreSQL移行予定

### 開発環境
- **IDE**: Visual Studio Code
- **パッケージ管理**: pip + requirements.txt
- **仮想環境**: Python venv
- **バージョン管理**: Git + GitHub

## 🚀 セットアップ方法

### 前提条件
- Python 3.9以上
- YouTube Data API キー（開発者用）

### 手順

1. **リポジトリをクローン**
   ```bash
   git clone https://github.com/purotakeman/car_ai_recommendation_2.git
   cd car_ai_recommendation_2
   ```

2. **仮想環境の作成と有効化**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **依存パッケージのインストール**
   ```bash
   pip install -r requirements.txt
   ```

4. **環境変数の設定**
   プロジェクトのルートディレクトリに `.env` ファイルを作成してください。
   このファイルは `.gitignore` により Git 管理から除外されます。
   ```text
   YOUTUBE_API_KEY=あなたのGoogle_APIキー
   ```

5. **アプリケーションの起動**
   ```bash
   python app.py
   ```

## 📊 使用方法

1. **条件設定**: トップページの検索フォームで以下の条件を入力
   - ボディタイプ（SUV、セダン、ハッチバックなど）
   - 駆動方式（2WD、4WDなど）
   - 燃料タイプ（ガソリン、ハイブリッドなど）
   - 上限価格
   - 燃費
   - 乗車定員

2. **検索実行**: 「車を診断する」ボタンをクリック

3. **結果確認**: 推薦スコア順に表示された車両一覧を確認

4. **詳細表示**: 気になる車両をクリックして詳細ページへ

5. **詳細情報**: スペック情報、維持費シミュレーション、レビューなどを確認

6. **お気に入り**: お気に入りボタンで車両を保存

## 🔌 API使用方法

### 全車両データ取得
```bash
GET /api/cars
```

### フィルタリング付きデータ取得
```bash
GET /api/cars?maker=トヨタ&body_type=SUV&max_price=500
```

### 特定車両データ取得
```bash
GET /api/cars/1
```

## 📂 プロジェクト構造
```
car_ai_recommendation/
├── app.py                    # Flaskのメインアプリケーション
├── requirements.txt          # 依存パッケージリスト
├── README.md                 # プロジェクト説明
├── requirements.md           # 要件定義書（本ドキュメント）
├── FUNCTIONAL_SPEC.md        # 機能仕様書
├── .env                      # APIキー設定(Git管理外) 
├── .gitignore                # 不要ファイル除外設定
│
├── /templates/               # 各画面のHTML
│   ├── index.html            # メインページ
│   ├── car_detail.html       # 車両詳細ページ
│   ├── favorites.html        # お気に入りページ
│   ├── 404.html              # 404エラーページ
│   └── 500.html              # 500エラーページ
│
├── /static/                  # 静的ファイル
│   ├── /css/                 # CSSファイル
│   │   ├── style.css         # メインスタイル
│   │   ├── detail.css        # 詳細ページスタイル
│   │   ├── enhanced.css      # 拡張機能スタイル
│   │   └── hybrid.css        # ハイブリッド診断スタイル
│   ├── /js/                  # JavaScriptファイル
│   │   ├── script.js         # メイン機能
│   │   ├── detail.js         # 詳細ページ機能
│   │   ├── enhanced.js       # 拡張機能
│   │   ├── script.js         # フォーム操作機能
│   │   └── hybrid.js         # ハイブリッド診断機能
│   └── /images/              # 画像ファイル
│       └── car_placeholder.png # 車両プレースホルダー画像
│
├── /data/                    # 車両DB(CSV)およびキャッシュ
│   ├── youtube_cache.json    # YouTube動画キャッシュ
│   └── car_data_base.csv     # 車両データCSV
│
└─── /utils/                  # 推薦・Youtube連携ロジック
    ├── filters.py            # フィルタリング関数
    ├── youtube.py            # Youtube連携関数
    └── recommendation.py     # 推薦ロジック
```

## 🔄 データ更新方法
車両データを更新する場合は、スクレイピングスクリプトを実行します：

```bash
# 仮想環境を有効化
source venv/bin/activate  # または venv\Scripts\activate (Windows)

# スクレイピングスクリプトを実行
python -m scraper.car_scraper

# または既存のCSVとマージ
python -m scraper.car_scraper --merge
```

## 🧪 開発・テスト

### ローカル開発
```bash
# デバッグモードで起動
export FLASK_ENV=development  # または set FLASK_ENV=development (Windows)
python app.py
```

### API テスト
```bash
# curlでAPIテスト
curl http://localhost:5000/api/cars
curl http://localhost:5000/api/cars/1
```

## 🎨 カスタマイズ

### CSSカスタマイズ
- `static/css/style.css`: メインページのスタイル
- `static/css/detail.css`: 詳細ページのスタイル

### JavaScript機能拡張
- `static/js/script.js`: メインページの機能
- `static/js/detail.js`: 詳細ページの機能

### 推薦ロジックの調整
- `utils/recommendation.py`: スコア計算アルゴリズムの修正

## 🚧 既知の制限事項
- 車両データはCSVファイルベースです。
- YouTube APIの無料枠制限により、1日の検索回数に上限があります（キャッシュ機能により最小化されています）。
- 一部、動画が見つからない車種はプレースホルダー画像が表示されます。

## 🤝 貢献方法
1. このリポジトリをフォーク
2. 新機能のブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチをプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## 📝 ライセンス
このプロジェクトは MIT ライセンスの下で公開されています。詳細は LICENSE ファイルをご覧ください。

## 📧 連絡先
- **プロジェクト管理者**: Your Name - email@example.com
- **プロジェクトリンク**: https://github.com/yourusername/car_ai_recommendation

## 📈 今後の発展予定
- **データベース移行**: CSV → SQLite/PostgreSQL
- **機械学習**: より高精度な推薦システム
- **外部API連携**: リアルタイムな価格情報取得
- **モバイルアプリ**: Progressive Web App (PWA) 対応

---
> ※本システムはポートフォリオ用に開発されています。実際の購入判断にはメーカー公式サイト等の最新情報をご確認ください。