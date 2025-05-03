# 推薦スコアの計算機能
"""
車両の推薦スコアを計算するモジュール
"""

def calculate_recommendation_scores(cars, user_preferences):
    """
    ユーザーの嗜好に基づいて各車の推薦スコアを計算する

    Parameters:
    -----------
    cars : list of dict
        車両情報のリスト
    user_preferences : dict
        ユーザーの嗜好情報(例: 価格重要度、燃費重要度、サイズ重要度、希望サイズなど)
    
    Returns:
    --------
    kist of dict
        推薦スコアが追加された車両情報のリスト
    """

    # デフォルト値の設定
    price_importance = float(user_preferences.get('price_importance', 0.5))
    fuel_economy_importance = float(user_preferences.get('fuel_economy_importance', 0.3))
    size_importance = float(user_preferences.get('size_importance', 0.2))
    preferred_size = user_preferences.get('preferred_size', 'medium')

    # サイズの好みに応じた評価基準を設定
    size_preferences = {
        'small': {'ideal_length': 4000, 'range': 400},
        'medium': {'ideal_length': 4500, 'range': 400},
        'large': {'ideal_length': 5000, 'range': 400},
    }
    size_pref = size_preferences.get(preferred_size, size_preferences['medium'])

    # 結果を格納する配列
    scored_cars = []

    # 最高・最低価格と燃費を計算(正規化のため)
    all_prices = [float(car['価格(万円)']) for car in cars if car['価格(万円)']]
    max_price = max(all_prices) if all_prices else 1000
    min_price = min(all_prices) if all_prices else 50

    all_fuel_economies = [float(car['燃費(km/L)']) for car in cars if car.get('燃費(km/L)')]
    max_fuel_economy = max(all_fuel_economies) if all_fuel_economies else 30
    min_fuel_economy = min(all_fuel_economies) if all_fuel_economies else 5

    for car in cars:
        # 各評価項目のスコアを計算(0~1の範囲)

        # 価格スコア(安いほど高スコア)
        price_score = 0.0
        if car['価格(万円)']:
            price = float(car['価格(万円)'])
            price_score = 1 - ((price - min_price) / (max_price - min_price) if max_price != min_price else 0)

        # 燃費スコア(高いほど高スコア)
        fuel_economy_score = 0.0
        if car.get('燃費(km/L)'):
            fuel_economy = float(car['燃費(km/L)'])
            fuel_economy_score = (fuel_economy - min_fuel_economy) / (max_fuel_economy - min_fuel_economy) if max_fuel_economy != min_fuel_economy else 0

         # サイズスコア（希望サイズに近いほど高スコア）
        size_score = 0.0
        if car.get('サイズ(mm)'):
            try:
                # "長さ×幅×高さ" 形式からサイズを抽出
                dimensions = car['サイズ(mm)'].split('×')
                if len(dimensions) >= 1:
                    length = int(dimensions[0])
                    # 希望サイズからの距離を計算し、スコア化
                    distance = abs(length - size_pref['ideal_length'])
                    size_score = max(0, 1 - (distance / size_pref['range']))
            except:
                pass
        
        # 総合スコアを計算（各項目を重要度で重み付け）
        total_score = (
            price_score * price_importance +
            fuel_economy_score * fuel_economy_importance +
            size_score * size_importance
        )
        
        # スコアを0～100の範囲に変換
        recommendation_score = round(total_score * 100)
        
        # 車両情報にスコアを追加
        car_with_score = car.copy()
        car_with_score['推薦スコア'] = recommendation_score
        
        scored_cars.append(car_with_score)
    
    # スコアの高い順にソート
    scored_cars.sort(key=lambda x: x['推薦スコア'], reverse=True)
    
    return scored_cars    