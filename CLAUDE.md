# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 概要

Flask 製の自動車推薦 Web アプリ（ポートフォリオ用）。車両データは CSV（`data/car_data_base.csv`、約1200件）で、DB はない。ドキュメント・コメント・コミットメッセージは日本語で書かれている。詳細な仕様は `FUNCTIONAL_SPEC.md`（機能仕様）と `requirements.md`（要件定義）にある。

## コマンド

```bash
# セットアップ（Windows）
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# ローカル起動（http://localhost:5000、PORT 環境変数で変更可。debug=False 固定）
python app.py

# 本番（Render 等）— Procfile
gunicorn app:app

# API の動作確認
curl http://localhost:5000/api/cars
curl http://localhost:5000/api/cars/1
```

- テスト・リンタは導入されていない。動作確認はアプリを起動してブラウザ／curl で行う。
- `.env` に `YOUTUBE_API_KEY` を設定する。未設定でもアプリは動き、動画欄がプレースホルダーになる。
- README に書かれている `python -m scraper.car_scraper` の `scraper` モジュールは存在しない。スクレイピング処理の実体は `utils/filters.py` の `CarScraper` で、`python utils/filters.py --confirm` で実行する（出力されるのはデモデータのみ）。

## アーキテクチャ

### リクエストの流れ
`app.py` が全ルートとデータ処理を持つ（Blueprint はない）。**リクエストのたびに `load_car_data()` で CSV を読み直す**ため、キャッシュはなく、CSV を編集すれば再起動しなくても反映される。読み込み時に列名の正規化（`燃費(km/L)電費(Wh/km)水素燃費(km/kg)` → `燃費(km/L)`）、欠損値の補完、`燃料の種類` の `" ("` → `"("` 置換を行い、dict のリストとして返す。

推薦処理の流れ：`filter_cars()`（絞り込み）→ `calculate_recommendation_scores()`（スコア付けとソート）→ `deduplicate_cars()`（メーカー＋車種が同じグレードの重複を除き、スコア最上位の1台だけ残す）→ 上位の車両に `get_car_videos()` で YouTube 情報を付ける。

### `/api/recommend` は3つのモードに対応
フロントの JS（`script.js`, `enhanced.js`, `hybrid.js`）はすべてこの1つのエンドポイントを使う。リクエストのフラグでモードが分かれる。
- `is_hybrid_diagnosis`（`user_profile` キーがある場合も含む）：`enhance_hybrid_preferences()` で重要度（`*_importance`）を絞り込み条件に変換し（例：燃費重要度 ≥0.8 なら燃料を HEV/PHEV/BEV/水素に限定）、スコアを計算する。レスポンスに `analysis` を付ける。上位20件を返す。
- `is_detailed_search`：**スコアは計算しない**。id 順に並べ、`page`/`per_page`（12件）でページ分けする。
- それ以外：シンプル診断。スコアを計算して上位20件を返す。

`/`（POST）はフォーム送信による従来の検索経路で、`index.html` をサーバー側で描画する。`/api/cars/batch` はお気に入りページが使う。

### 推薦エンジン（`utils/recommendation.py`）
`EnhancedCarRecommendationEngine` がユーザー嗜好からプロファイル（family/commuter/luxury/eco/sporty/general）を判定する。その後、項目別スコア（価格・燃費・サイズ・安全・維持費・ブランド・環境・用途適合）を 0–100 で出し、プロファイルごとの重みに重要度（1–5、3 が基準）を掛けて調整した加重平均を `推薦スコア` とする。車両 dict には `推薦スコア`・`詳細スコア`・`推薦理由` が追加される。安全装備の点数は `SAFETY_EQUIPMENT_SCORES`、ブランド階層は `brand_tiers` で管理しており、メーカー名はカタカナ表記と英字表記（`TOYOTA` など）の両方を登録している。

### フロントエンド
- 各テンプレートは `script.js` を共通で読み込み、ページごとの JS を追加で読む（index: `enhanced.js` + `hybrid.js`、詳細: `detail.js`、お気に入り: `favorites.js`）。
- お気に入りは `localStorage` の `carFavorites`（車両 id の配列）に保存する。サーバー側には保存しない。`/favorites` はテンプレートを返すだけ。

### YouTube 連携（`utils/youtube.py`）
`data/youtube_cache.json`（gitignore 対象）にファイルでキャッシュする。キーは `{メーカー}_{車種}_v2`。API 無料枠を節約するため、キャッシュに当たれば API は呼ばない。キャッシュ形式を変えるときはキーのサフィックスを上げる。

## データの注意点

- CSV の列名は日本語で、コード全体が直接参照している。列名を変えるときは `app.py`、`utils/recommendation.py`、テンプレート、JS をすべて確認すること。
- `価格帯(万円)` 列は名前に反して **円単位** の範囲文字列（例：`5100000~10650000`）。`filter_cars()` と `format_currency` が閾値（10000 / 100000）で万円に換算しているため、単位を前提にした処理を書くときは注意する。
- 燃料フィルタは部分一致（`ft in car_fuel`）。`index.html` のチェックボックスの value（`レギュラー`, `(HEV)` など）は CSV の `燃料の種類` の値（`レギュラー(HEV)` など）と一致している必要がある。レギュラー／ハイオク／HEV などは意図的に統合せず、別々に扱っている。
- `id` 列が車両の主キーで、詳細ページの URL（`/car/<id>`）とお気に入りに使われている。
