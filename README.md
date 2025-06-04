# AI自動車診断システム

## 📝 プロジェクト概要
AI自動車診断システムは、自動車の知識があまりないユーザーでも、自分に最適なクルマを見つけられるウェブサービスです。ユーザーの希望（ボディタイプ、駆動方式、価格など）に基づき、AI的なロジックで車を推薦・フィルタリングします。

## 🎯 目的
- 自動車選びの複雑さを解消し、初心者でも適切な選択ができるようサポート
- 様々な条件や好みから個々のニーズに最適化された車両を推薦
- 詳細な車両情報をわかりやすく整理して提供
- コストや維持費も含めた総合的な判断材料を提供

## 🌟 主要機能

### 現在実装済み
- 🔍 **複数条件での車両検索・フィルタリング機能**
- 🚗 **車両情報の一覧表示と詳細表示**
- 💯 **ユーザーの嗜好に基づく車両推薦スコアの計算**
- 📊 **維持費シミュレーション**
- 💾 **お気に入り機能（ローカルストレージ）**
- 🔄 **検索結果の並び替え機能**
- 🔌 **RESTful API（JSON形式）による車両データ提供**
- 📱 **レスポンシブデザイン対応**

### 開発予定
- 👤 **ユーザーアカウント管理**
- 🤖 **AIによる自然言語での車両推薦**
- 📂 **詳細なユーザーレビューとコミュニティ機能**
- 🔗 **YouTubeレビュー動画の統合**
- 🌐 **SNS共有機能**
- 🔄 **自動データ更新システム**

## 🛠️ 技術スタック

### バックエンド
- **言語**: Python 3.9+
- **Webフレームワーク**: Flask 2.3.3
- **データ処理**: Pandas 2.0.3
- **Webスクレイピング**: BeautifulSoup4 4.12.2, Requests 2.31.0

### フロントエンド
- **マークアップ**: HTML5, Jinja2テンプレート
- **スタイリング**: CSS3（レスポンシブデザイン）
- **インタラクション**: JavaScript (ES6+)
- **アイコン**: Font Awesome 5.15.4

### API・通信
- **API形式**: RESTful API（JSON形式）
- **エンドポイント**: `/api/cars`, `/api/cars/<id>`
- **データ交換**: JSON（フロントエンド⇔バックエンド間通信）

### データ管理
- **現在**: CSVファイル
- **将来**: SQLite または PostgreSQL移行予定

### 開発環境
- **IDE**: Visual Studio Code
- **パッケージ管理**: pip + requirements.txt
- **仮想環境**: Python venv
- **バージョン管理**: Git + GitHub

## 🚀 インストール方法

### 前提条件
- Python 3.9以上
- pip (Pythonパッケージマネージャー)
- 仮想環境(venv, virtualenv など)を推奨

### セットアップ手順

1. **リポジトリをクローン**
   ```bash
   git clone https://github.com/yourusername/car_ai_recommendation.git
   cd car_ai_recommendation
   ```

2. **仮想環境の作成と有効化**
   ```bash
   python -m venv venv
   
   # Windowsの場合
   venv\Scripts\activate
   
   # macOS/Linuxの場合
   source venv/bin/activate
   ```

3. **依存パッケージのインストール**
   ```bash
   pip install -r requirements.txt
   ```

4. **アプリケーションの起動**
   ```bash
   python app.py
   ```

5. **ブラウザでアクセス**
   ```
   http://127.0.0.1:5000/
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

### レスポンス例
```json
[
  {
    "id": 1,
    "メーカー": "トヨタ",
    "車種": "プリウス",
    "ボディタイプ": "ハッチバック",
    "価格(万円)": 250,
    "燃費(km/L)": 32.6,
    "推薦スコア": 85
  }
]
```

## 📂 プロジェクト構造
```
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
│   │   ├── style.css         # メインスタイル
│   │   └── detail.css        # 詳細ページスタイル
│   ├── /js/                  # JavaScriptファイル
│   │   ├── script.js         # メイン機能
│   │   └── detail.js         # 詳細ページ機能
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
- 車両データは固定（19台）
- ユーザー認証機能未実装
- 画像データなし
- 実際の中古車価格との連携なし

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

> このプロジェクトは個人の学習・ポートフォリオ用に作成されています。掲載されている車両情報は参考用であり、実際の購入判断には公式情報をご確認ください。