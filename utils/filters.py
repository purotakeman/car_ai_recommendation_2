import pandas as pd

def filter_cars(cars_data, filters):
    """
    車両データを指定されたフィルターに基づいてフィルタリングする

    parameters:
    -----------
    cars_data : list of dict
        車両データのリスト
    filters : dict
        フィルター条件を含む辞書
        {
            'body_type': list, # ボディタイプのリスト
            'drive_type': list, # 駆動方式のリスト
            'max_price': int, # 最大価格
            'fuel_type': list, # 燃料タイプのリスト
            'min_fuel_economy': float, # 最低燃費
            'min_seats': int, # 最低乗車人数
        }
    Returns:
    -----------
    list of dict
        フィルタリングされた車両データのリスト
    """
    filtered_data = []

    for car in cars_data:
        # 全てのフィルター条件を満たすかチェック
        include_car = True

        # ボディタイプのフィルター
        if 'body_type' in filters and filters['body_type'] and car.get('ボディタイプ') not in filters['body_type']:
            include_car = False

        # 駆動方式のフィルター
        if include_car and 'drive_type' in filters and filters['drive_type'] and car.get('駆動方式') not in filters['drive_type']:
            include_car = False

        # 最大価格のフィルター
        if include_car and 'max_price' in filters and filters['max_price']:
            try:
                car_price = float(car.get('価格(万円)', 0))
                if car_price > float(filters['max_price']):
                    include_car = False
            except (ValueError, TypeError):
                # 価格が数値でない場合はスキップ
                pass

        # 燃料タイプのフィルター
        if include_car and 'fuel_type' in filters and filters['fuel_type'] and car.get('燃料の種類') not in filters['fuel_type']:
            include_car = False

        # 最低燃費のフィルター 
        if include_car and 'min_fuel_economy' in filters and filters['min_fuel_economy']:
            try:
                fuel_economy = float(car.get('燃費(km/L)', 0))
                if fuel_economy < float(filters['min_fuel_economy']):
                    include_car = False
            except (ValueError, TypeError):
                # 燃費が数値でない場合はスキップ
                pass

        # 最低乗車人数のフィルター
        if include_car and 'min_seats' in filters and filters['min_seats']:
            try:
                seats = int(car.get('乗車人数', 0))
                if seats < int(filters['min_seats']):
                    include_car = False
            except (ValueError, TypeError):
                 # 乗車人数が数値出ない場合はスキップ
                pass

            # 全ての条件を満たしている場合は結果に追加
        if include_car:
            filtered_data.append(car)

    return filtered_data

def rank_cars(cars_data, preferences):
    """
    車両データを指定された条件に基づいてランク付けする

    Parameters:
    -----------
    cars_data : list of dict
        車両でデータのリスト
    preference : dict
        ユーザーの好みを表す辞書
        {
            'price_importance': float, # 価格の重要度(0-1)
            'fuel_economy_importance': float, # 燃費の重要度(0-1)
            'size_importance': float, # サイズの重要度(0-1)
            'preferred_size': str, # 好みのサイズ('small', 'medium', 'large')
        }

    Returns:
    -------
    list of dict
        スコア付きでランク付けされた車両データのリスト
    """
    ranked_cars = []

    # 価格、燃費の最大・最小値を特定(正規化用)
    price_values = [float(car.get('価格(万円)', 0)) for car in cars_data if car.get('価格(万円)')]
    fuel_values = [float(car.get('燃費(km/L)', 0)) for car in cars_data if car.get('燃費(km/L)')]

    max_price = max(price_values) if price_values else 1000
    min_price = min(price_values) if price_values else 0            
    max_fuel = max(fuel_values) if fuel_values else 30
    min_fuel = min(fuel_values) if fuel_values else 0   

    for car in cars_data:
        score = 0

          # 価格スコア(低いほど良い) - 反転して計算
        if 'price_importance' in preferences and car.get('価格(万円)'):
            try:
                price = float(car.get('価格(万円)'))
                # 価格を0-1の範囲に正規化し、反転する(低いほど良い)
                normalized_price = 1 - ((price - min_price) / (max_price - min_price)) if max_price != min_price else 0.5
                score += normalized_price * preferences['price_importance']
            except (ValueError, TypeError):
                pass                           
          # 燃費スコア(高いほどよい)
        if 'fuel_economy_importance' in preferences and car.get('燃費(km/L)'):
            try:
                fuel_economy = float(car.get('燃費(km/L)'))
                # 燃費を0-1の範囲に正規化する(高いほどよい)
                normalized_fuel = (fuel_economy - min_fuel) / (max_fuel - min_fuel) if max_fuel != min_fuel else 0.5    
                score += normalized_fuel * preferences['fuel_economy_importance']
            except (ValueError, TypeError):
                pass

        # サイズスコア(好みのサイズに近いほどよい)
        if 'size_importance' in preferences and preferences.get('preferred_size') and car.get('サイズ(mm)'):
            try:
                # サイズから全長を取得(最初の数値)
                size_text = car.get('サイズ(mm)')
                length = int(size_text.split('x')[0])

                # 好みのサイズに応じたスコア
                size_score = 0
                if preferences['preferred_size'] == 'small' and length < 4500:
                    size_score = 1.0
                elif preferences['preferred_size'] == 'medium' and 4500<= length <= 4800:
                    size_score = 1.0
                elif preferences['preferred_size'] == 'large' and length > 4800:
                    size_score = 1.0
                else:
                    # どれにも当てはまらない場合は、近さに応じてスコアを下げる
                    if preferences['preferred_size'] == 'small':
                        size_score = max(0, 1 - (length - 4500) / 1000)
                    elif preferences['preferred_size'] == 'medium':
                        size_score = max(0, 1 - min(abs(length - 4500), abs(length - 4800)) / 500)
                    elif preferences['preferred_size'] == 'large':
                        size_score = max(0, 1 - (4800 - length) / 1000)

                score += size_score * preferences['size_importance']
            except (ValueError, TypeError, IndexError):
                pass

        # スコア付き車情報を結果に追加
        car_with_score = car.copy()
        car_with_score['推薦スコア'] = round(score * 100, 1) # パーセント表示に変換
        ranked_cars.append(car_with_score)

    # スコアの高い順にソート
    ranked_cars = sorted(ranked_cars, key=lambda x: x.get('推薦スコア', 0), reverse=True)

    return ranked_cars

def get_car_recommendations(cars_data, user_inputs):
    """
    ユーザー入力に基づいて車の推薦を行う

    Parameters:
    -----------
    cars_data : list of dict
        車両データのリスト
    user_inputs : dict
        ユーザーの入力と好みを表す辞書

    Returns:
    --------
    list of dict
        推薦された車両のリスト
    """

    # フィルター条件を抽出
    filters = {
        'body_type': user_inputs.get('body_type', []),
        'drive_type': user_inputs.get('drive_type', []),
        'max_price': user_inputs.get('max_price'),
        'fuel_type': user_inputs.get('fuel_type', []),
        'min_fuel_economy': user_inputs.get('min_fuel_economy'),
        'min_seats': user_inputs.get('min_seats')
    }

    # 好み/重み付け条件を抽出
    preferences = {
        'price_importance': user_inputs.get('price_importance', 0.5),
        'fuel_economy_importance': user_inputs.get('fuel_economy_importance', 0.3),
        'size_importance': user_inputs.get('size_importance', 0.2),
        'preferred_size': user_inputs.get('preferred_size', 'medium')
    }

    # フィルタリングと推薦
    filtered_cars = filter_cars(cars_data, filters)
    recommended_cars = rank_cars(filtered_cars, preferences)

    return recommended_cars
