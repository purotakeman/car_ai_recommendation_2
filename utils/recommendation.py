# 推薦スコアの計算機能
"""
改善された車両推薦アルゴリズム
-多角的な評価指標
-ユーザープロファイル別推薦
-用途別最適化
-動的重み付け
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedCarRecommendationEngine:
    """
    改善された車両推薦エンジン
    """

    def __init__(self):
        # ユーザープロファイル定義
        self.user_profiles = {
            'family': { # ファミリー向け
                'priorities': {
                    'safety':0.25,     # 安全性重視
                    'space': 0.20,     # 室内空間重視
                    'fuel_economy': 0.20, # 燃費重視
                    'price' : 0.15,       # 価格重視
                    'reliability': 0.10   #信頼性重視
                },
                'preferred_body_types': ['ミニバン', 'SUV', 'ハッチバック'],
                'min_seats': 5
            },
            'commuter': {  # 通勤向け
                'priorities': {
                    'fuel_economy': 0.30,  # 燃費最重視
                    'price': 0.25,         # 価格重視
                    'maintenance': 0.20,   # 維持費重視
                    'size': 0.15,          # コンパクト重視
                    'reliability': 0.10
                },
                'preferred_body_types': ['ハッチバック', '軽自動車', 'セダン'],
                'max_price': 300
            },
            'luxury': {  # 高級志向
                'priorities': {
                    'comfort': 0.25,      # 快適性重視
                    'performance': 0.20,  # 性能重視
                    'brand': 0.20,        # ブランド重視
                    'safety': 0.15,       # 安全性重視
                    'design': 0.20        # デザイン重視
                },
                'preferred_body_types': ['セダン', 'SUV', 'オープンカー'],
                'min_price': 400
            },
            'eco': {  # エコ志向
                'priorities': {
                    'fuel_economy': 0.35,  # 燃費最重視
                    'environmental': 0.25, # 環境性能重視
                    'price': 0.20,         # 価格重視
                    'maintenance': 0.20    # 維持費重視
                },
                'preferred_fuel_types': ['ハイブリッド', 'EV', 'PHEV']
            },
            'sporty': {  # スポーツ志向
                'priorities': {
                    'performance': 0.30,   # 性能最重視
                    'design': 0.25,        # デザイン重視
                    'handling': 0.20,      # ハンドリング重視
                    'brand': 0.15,         # ブランド重視
                    'uniqueness': 0.10     # 個性重視
                },
                'preferred_body_types': ['オープンカー', 'ハッチバック', 'セダン']
            }
        }
        
        # ブランド階層（信頼性・ブランド力の評価用）
        self.brand_tiers = {
            'premium': ['レクサス', 'メルセデス・ベンツ', 'BMW', 'アウディ', 'ボルボ'],
            'mainstream': ['トヨタ', 'ホンダ', '日産', 'マツダ', 'スバル'],
            'value': ['ダイハツ', 'スズキ', '三菱'],
            'specialty': ['テスラ', 'ポルシェ', 'フェラーリ']
        }
    








    def calculate_enhanced_recommendation_scores(self, cars: List[Dict], user_preferences: Dict) -> List[Dict]:
        """
        ユーザーの嗜好に基づいて各車の推薦スコアを計算する
        
        Parameters:
        -----------
        cars : List[Dict]
            車両情報のリスト
        user_preferences : Dict
            ユーザーの嗜好情報
            
        Returns:
        --------
        List[Dict]
            推薦スコア付きの車両リスト
        """
        logger.info(f"推薦スコア計算開始: {len(cars)}台の車両を分析")
        
        # ユーザープロファイルの特定
        user_profile = self._identify_user_profile(user_preferences)
        logger.info(f"特定されたユーザープロファイル: {user_profile}")
        
        # 各車両の詳細スコア計算
        scored_cars = []
        
        for car in cars:
            detailed_scores = self._calculate_detailed_scores(car, user_preferences, user_profile)
            final_score = self._calculate_weighted_final_score(detailed_scores, user_profile)
            
            # 車両情報にスコア情報を追加
            enhanced_car = car.copy()
            enhanced_car['推薦スコア'] = final_score
            enhanced_car['詳細スコア'] = detailed_scores
            enhanced_car['推薦理由'] = self._generate_recommendation_reason(car, detailed_scores, user_profile)
            
            scored_cars.append(enhanced_car)
        
        # 最終スコアでソート
        scored_cars.sort(key=lambda x: x['推薦スコア'], reverse=True)
        
        logger.info("推薦スコア計算完了")
        return scored_cars

    def _identify_user_profile(self, user_preferences: Dict) -> str:
        """
        ユーザーの嗜好からプロファイルを特定
        """
        # 選択されたボディタイプや価格帯からプロファイルを推測
        body_types = user_preferences.get('body_types', [])
        max_price = float(user_preferences.get('max_price', 500)) if user_preferences.get('max_price') else 500
        min_seats = int(user_preferences.get('min_seats', 2)) if user_preferences.get('min_seats') else 2
        fuel_types = user_preferences.get('fuel_types', [])
        
        profile_scores = {}
        
        # ファミリー向け判定
        family_score = 0
        if min_seats >= 5:
            family_score += 30
        if any(bt in ['ミニバン', 'SUV'] for bt in body_types):
            family_score += 20
        if max_price <= 400:
            family_score += 10
        profile_scores['family'] = family_score
        
        # 通勤向け判定
        commuter_score = 0
        if max_price <= 300:
            commuter_score += 25
        if any(bt in ['ハッチバック', '軽自動車'] for bt in body_types):
            commuter_score += 20
        if float(user_preferences.get('fuel_economy_importance', 0)) > 0.5:
            commuter_score += 15
        profile_scores['commuter'] = commuter_score
        
        # 高級志向判定
        luxury_score = 0
        if max_price >= 500:
            luxury_score += 30
        if any(bt in ['セダン', 'オープンカー'] for bt in body_types):
            luxury_score += 15
        profile_scores['luxury'] = luxury_score
        
        # エコ志向判定
        eco_score = 0
        if any(ft in ['ハイブリッド', 'EV', 'PHEV'] for ft in fuel_types):
            eco_score += 35
        if float(user_preferences.get('fuel_economy_importance', 0)) > 0.7:
            eco_score += 20
        profile_scores['eco'] = eco_score
        
        # スポーツ志向判定
        sporty_score = 0
        if any(bt in ['オープンカー'] for bt in body_types):
            sporty_score += 30
        if min_seats <= 4:
            sporty_score += 15
        profile_scores['sporty'] = sporty_score
        
        # 最高スコアのプロファイルを返す（最低しきい値以上の場合）
        best_profile = max(profile_scores, key=profile_scores.get)
        if profile_scores[best_profile] >= 20:
            return best_profile
        else:
            return 'general'  # 汎用プロファイル

    def _calculate_detailed_scores(self, car: Dict, user_preferences: Dict, user_profile: str) -> Dict:
        """
        車両の詳細スコアを計算
        """
        scores = {}
        
        # 1. 価格スコア（0-100）
        scores['price'] = self._calculate_price_score(car, user_preferences)
        
        # 2. 燃費スコア（0-100）
        scores['fuel_economy'] = self._calculate_fuel_economy_score(car)
        
        # 3. サイズ適合度スコア（0-100）
        scores['size'] = self._calculate_size_score(car, user_preferences)
        
        # 4. 安全性スコア（0-100）
        scores['safety'] = self._calculate_safety_score(car)
        
        # 5. 維持費スコア（0-100）
        scores['maintenance'] = self._calculate_maintenance_score(car)
        
        # 6. ブランド信頼性スコア（0-100）
        scores['brand'] = self._calculate_brand_score(car)
        
        # 7. 環境性能スコア（0-100）
        scores['environmental'] = self._calculate_environmental_score(car)
        
        # 8. 用途適合度スコア（0-100）
        scores['purpose_fit'] = self._calculate_purpose_fit_score(car, user_profile)
        
        return scores

    def _calculate_price_score(self, car: Dict, user_preferences: Dict) -> int:
        """価格スコア計算"""
        try:
            price = float(car.get('価格(万円)', 0))
            max_price = float(user_preferences.get('max_price', 1000)) if user_preferences.get('max_price') else 1000
            
            if price == 0:
                return 50  # 価格不明の場合は中間点
            
            if price <= max_price:
                # 予算内の場合、安いほど高スコア
                ratio = price / max_price
                return int(100 * (1 - ratio * 0.8))  # 80%まで減点
            else:
                # 予算超過の場合、大幅減点
                over_ratio = (price - max_price) / max_price
                return max(0, int(50 - over_ratio * 100))
                
        except (ValueError, TypeError):
            return 50

    def _calculate_fuel_economy_score(self, car: Dict) -> int:
        """燃費スコア計算"""
        try:
            fuel_economy = float(car.get('燃費(km/L)', 0))
            fuel_type = car.get('燃料の種類', '')
            
            if fuel_economy == 0:
                return 30
            
            # 燃料タイプ別の基準値調整
            if fuel_type == 'EV':
                # EVの場合は特別に高評価
                return 95
            elif fuel_type in ['ハイブリッド', 'PHEV']:
                # ハイブリッド系は25km/L以上で満点
                base_score = min(100, int(fuel_economy * 4))
            else:
                # ガソリン車は20km/L以上で満点
                base_score = min(100, int(fuel_economy * 5))
            
            return max(10, base_score)
            
        except (ValueError, TypeError):
            return 30

    def _calculate_size_score(self, car: Dict, user_preferences: Dict) -> int:
        """サイズ適合度スコア計算"""
        try:
            size_str = car.get('サイズ(mm)', '')
            preferred_size = user_preferences.get('preferred_size', 'medium')
            
            if not size_str:
                return 50
            
            # サイズから全長を抽出
            import re
            size_match = re.search(r'(\d+)×', str(size_str))
            if not size_match:
                return 50
                
            length = int(size_match.group(1))
            
            # 希望サイズ別の評価
            size_preferences = {
                'small': {'ideal': 3800, 'range': 600},   # 軽自動車・コンパクト
                'medium': {'ideal': 4500, 'range': 700},  # ミドルサイズ
                'large': {'ideal': 5000, 'range': 800}    # 大型車
            }
            
            pref = size_preferences.get(preferred_size, size_preferences['medium'])
            distance = abs(length - pref['ideal'])
            
            if distance <= pref['range']:
                score = 100 - int((distance / pref['range']) * 50)
            else:
                score = max(0, 50 - int((distance - pref['range']) / 200))
            
            return max(0, min(100, score))
            
        except (ValueError, TypeError):
            return 50

    def _calculate_safety_score(self, car: Dict) -> int:
        """安全性スコア計算"""
        try:
            safety_rating = float(car.get('安全評価', 3))
            # 5段階評価を100点満点に変換
            return int(safety_rating * 20)
        except (ValueError, TypeError):
            return 60  # デフォルト値

    def _calculate_maintenance_score(self, car: Dict) -> int:
        """維持費スコア計算"""
        try:
            tax = float(car.get('自動車税(円)', 50000))
            displacement = float(car.get('排気量', 1500))
            fuel_type = car.get('燃料の種類', 'ガソリン')
            
            # 自動車税による評価（安いほど高スコア）
            tax_score = max(0, 100 - int(tax / 1000))
            
            # 排気量による評価（小さいほど維持費安い）
            displacement_score = max(0, 100 - int(displacement / 50))
            
            # 燃料タイプによる調整
            fuel_bonus = {
                'EV': 20,
                'ハイブリッド': 15,
                'PHEV': 10,
                'ガソリン': 0,
                'ディーゼル': 5
            }
            
            final_score = (tax_score + displacement_score) // 2 + fuel_bonus.get(fuel_type, 0)
            return max(0, min(100, final_score))
            
        except (ValueError, TypeError):
            return 50

    def _calculate_brand_score(self, car: Dict) -> int:
        """ブランド信頼性スコア計算"""
        maker = car.get('メーカー', '')
        
        for tier, brands in self.brand_tiers.items():
            if maker in brands:
                if tier == 'premium':
                    return 95
                elif tier == 'mainstream':
                    return 85
                elif tier == 'value':
                    return 75
                elif tier == 'specialty':
                    return 90
        
        return 70  # 不明ブランドのデフォルト

    def _calculate_environmental_score(self, car: Dict) -> int:
        """環境性能スコア計算"""
        fuel_type = car.get('燃料の種類', 'ガソリン')
        fuel_economy = float(car.get('燃費(km/L)', 15))
        
        # 燃料タイプ別基本スコア
        base_scores = {
            'EV': 100,
            'PHEV': 85,
            'ハイブリッド': 80,
            'ディーゼル': 60,
            'ガソリン': 40
        }
        
        base_score = base_scores.get(fuel_type, 40)
        
        # 燃費による調整
        if fuel_type != 'EV':
            fuel_bonus = min(20, int((fuel_economy - 10) * 2))
            base_score += fuel_bonus
        
        return max(0, min(100, base_score))

    def _calculate_purpose_fit_score(self, car: Dict, user_profile: str) -> int:
        """用途適合度スコア計算"""
        if user_profile == 'general':
            return 70
        
        profile_data = self.user_profiles.get(user_profile, {})
        body_type = car.get('ボディタイプ', '')
        seats = int(car.get('乗車定員', 5))
        price = float(car.get('価格(万円)', 300))
        fuel_type = car.get('燃料の種類', 'ガソリン')
        
        score = 50  # 基本点
        
        # ボディタイプ適合度
        preferred_bodies = profile_data.get('preferred_body_types', [])
        if body_type in preferred_bodies:
            score += 30
        
        # 乗車定員チェック
        min_seats = profile_data.get('min_seats', 0)
        if seats >= min_seats:
            score += 10
        
        # 価格帯チェック
        min_price = profile_data.get('min_price', 0)
        max_price = profile_data.get('max_price', 10000)
        if min_price <= price <= max_price:
            score += 15
        
        # 燃料タイプチェック
        preferred_fuels = profile_data.get('preferred_fuel_types', [])
        if preferred_fuels and fuel_type in preferred_fuels:
            score += 20
        
        return max(0, min(100, score))

    def _calculate_weighted_final_score(self, detailed_scores: Dict, user_profile: str) -> int:
        """重み付け最終スコア計算"""
        if user_profile == 'general':
            # 汎用プロファイルの場合は均等重み
            weights = {
                'price': 0.2,
                'fuel_economy': 0.2,
                'size': 0.15,
                'safety': 0.15,
                'maintenance': 0.15,
                'brand': 0.1,
                'environmental': 0.05
            }
        else:
            # 特定プロファイルの重み
            profile_priorities = self.user_profiles[user_profile]['priorities']
            weights = {
                'price': profile_priorities.get('price', 0.1),
                'fuel_economy': profile_priorities.get('fuel_economy', 0.1),
                'size': profile_priorities.get('size', 0.1),
                'safety': profile_priorities.get('safety', 0.1),
                'maintenance': profile_priorities.get('maintenance', 0.1),
                'brand': profile_priorities.get('brand', 0.1),
                'environmental': profile_priorities.get('environmental', 0.1),
                'purpose_fit': 0.3  # 用途適合度は常に重要
            }
        
        final_score = 0
        total_weight = 0
        
        for factor, weight in weights.items():
            if factor in detailed_scores:
                final_score += detailed_scores[factor] * weight
                total_weight += weight
        
        # 正規化
        if total_weight > 0:
            final_score = final_score / total_weight
        
        return max(0, min(100, int(final_score)))

    def _generate_recommendation_reason(self, car: Dict, detailed_scores: Dict, user_profile: str) -> str:
        """推薦理由を生成"""
        reasons = []
        
        # 高得点要因の特定
        high_score_factors = {k: v for k, v in detailed_scores.items() if v >= 80}
        
        if 'fuel_economy' in high_score_factors:
            fuel_economy = car.get('燃費(km/L)', 0)
            fuel_type = car.get('燃料の種類', '')
            if fuel_type == 'EV':
                reasons.append("電気自動車なので環境に優しく、ランニングコストも抑えられます")
            elif fuel_type in ['ハイブリッド', 'PHEV']:
                reasons.append(f"優れた燃費性能（{fuel_economy}km/L）で経済的です")
            else:
                reasons.append(f"燃費が良好（{fuel_economy}km/L）で日常使いに経済的です")
        
        if 'safety' in high_score_factors:
            safety = car.get('安全評価', 0)
            reasons.append(f"高い安全評価（{safety}/5）を獲得しており、安心して運転できます")
        
        if 'maintenance' in high_score_factors:
            tax = car.get('自動車税(円)', 0)
            if tax <= 15000:
                reasons.append("維持費が安く、年間の自動車税も抑えられます")
        
        if 'brand' in high_score_factors:
            maker = car.get('メーカー', '')
            if maker in self.brand_tiers['premium']:
                reasons.append("プレミアムブランドならではの品質と信頼性があります")
            elif maker in self.brand_tiers['mainstream']:
                reasons.append("信頼性の高い国産メーカーで、アフターサービスも充実しています")
        
        if 'purpose_fit' in high_score_factors:
            if user_profile == 'family':
                reasons.append("ファミリー用途に最適な装備と空間を備えています")
            elif user_profile == 'commuter':
                reasons.append("通勤利用に適したコンパクトサイズと経済性を兼ね備えています")
            elif user_profile == 'eco':
                reasons.append("環境性能に優れ、エコ志向の方におすすめです")
        
        if not reasons:
            reasons.append("総合的にバランスの取れた良い車です")
        
        return "、".join(reasons[:3])  # 最大3つの理由

# 既存の関数を置き換える関数
def calculate_recommendation_scores(cars, user_preferences):
    """
    推薦スコア計算のメイン関数（ハイブリッド診断対応）
    """
    return enhanced_calculate_recommendation_scores(cars, user_preferences)
