import os
import requests
import json
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数からAPIキーを取得
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

CACHE_FILE = "data/youtube_cache.json"

def get_car_videos(manufacturer, car_model, count=5):
    """
    メーカー名と車種名からYouTubeの試乗動画(日本語)を検索する
    """
    # キャッシュの読み込み
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache = json.load(f)
        except:
            cache = {}

    # キャッシュキー。複数件取得に対応するため、キーに件数を含めるか、
    # 常にリストで保存するように形式を変更する
    cache_key = f"{manufacturer}_{car_model}_v2" # バージョンを上げて古いキャッシュ（単一オブジェクト）を無視する
    if cache_key in cache:
        return cache[cache_key][:count]

    # APIリクエスト
    # クエリの厳密性を高めるために、車種名を引用符で囲むことを検討。
    # ただし、モデル名が「カローラ」のように広範な場合、「カローラ クロス」などもヒットしやすいため、
    # タイトルチェックでフィルタリングを行う。
    search_query = f"{manufacturer} {car_model} 試乗 レビュー モータージャーナリスト"
    
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'key': YOUTUBE_API_KEY,
        'q': search_query,
        'part': 'snippet',
        'maxResults': 10, # 多めに取得して後でフィルタリング
        'order': 'relevance', # 関連性優先に変更（ユーザーの要望）
        'relevanceLanguage': 'ja',
        'regionCode': 'JP',
        'type': 'video'
    }

    try:
        if not YOUTUBE_API_KEY:
            return []

        response = requests.get(url, params=params)
        data = response.json()

        videos = []
        if 'items' in data:
            for item in data['items']:
                title = item['snippet']['title']
                video_id = item['id']['videoId']
                
                # 関連性を高めるための簡易フィルタリング：
                # 車種名がタイトルに含まれているかチェック（大文字小文字無視、半角全角無視は簡易的に）
                # 完璧ではないが、全く違う車種が混ざるのを抑制できる
                if car_model.lower() in title.lower() or car_model.replace(" ", "") in title.replace(" ", ""):
                    videos.append({
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'title': title
                    })
            
            # フィルタリングの結果が空、または少ない場合は、車種名チェックを緩めて再度追加
            if len(videos) < 2:
                for item in data['items']:
                    video_id = item['id']['videoId']
                    video_data = {
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'title': item['snippet']['title']
                    }
                    if video_data not in videos:
                        videos.append(video_data)

            # キャッシュに保存
            cache[cache_key] = videos
            # キャッシュファイルが大きくなりすぎないよう古いキーを消すなどの処理が必要かもしれないが、
            # 現状はそのまま保存
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=4)

            return videos[:count]
            
    except Exception as e:
        print(f"YouTube検索エラー ({manufacturer} {car_model}): {e}")

    return []






















