# フィルタ処理やデータ変換の関数群
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import re

class CarScraper:
    def __init__(self, output_path="data/raw_data.csv"):
        """
        車両情報をウェブサイトからスクレイピングするクラス

        Parameters:
        -----------
        output_path : str
            スクレイピングした結果を保存するcsvファイルのパス
        """
        self.output_path = output_path
        self.headers = {
            # User-Agentを最新のものに更新
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 
        }
        
        # 【修正】DataFrame のスペルミス修正
        self.data = pd.DataFrame(columns=[
            'id', 'メーカー', '車種', 'ボディタイプ', '駆動方式', '価格(万円)', 
            '排気量', '年式', 'モデル', '安全評価', '燃費(km/L)', '燃料の種類', 
            '自動車税(円)', '乗車定員', '中古相場(万円)', 'サイズ(mm)'
        ])

        # 【修正】os.path.dirname のスペルミス修正
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    def scrape_simple_demo_data(self, limit=5):
        """
        デモ用の車両データを生成する（実際のスクレイピングが困難な場合の代替手段）
        
        Parameters:
        -----------
        limit : int
            生成する車両数の上限
        """
        print(f"デモ用車両データを生成します（最大{limit}件）...")
        
        # デモ用データセット
        demo_cars = [
            {
                'メーカー': 'トヨタ', '車種': 'プリウス', 'ボディタイプ': 'ハッチバック',
                '駆動方式': '2WD', '価格(万円)': '250', '排気量': '1800',
                '年式': '2025', '燃費(km/L)': '32.6', '燃料の種類': 'ハイブリッド',
                '自動車税(円)': '34500', '乗車定員': '5', '中古相場(万円)': '120~160',
                'サイズ(mm)': '4600×1800×1450'
            },
            {
                'メーカー': 'ホンダ', '車種': 'ヴェゼル', 'ボディタイプ': 'SUV',
                '駆動方式': '2WD', '価格(万円)': '280', '排気量': '1500',
                '年式': '2024', '燃費(km/L)': '27.0', '燃料の種類': 'ハイブリッド',
                '自動車税(円)': '39500', '乗車定員': '5', '中古相場(万円)': '180~230',
                'サイズ(mm)': '4330×1790×1590'
            },
            {
                'メーカー': '日産', '車種': 'セレナ', 'ボディタイプ': 'ミニバン',
                '駆動方式': '2WD', '価格(万円)': '320', '排気量': '2000',
                '年式': '2024', '燃費(km/L)': '18.0', '燃料の種類': 'ガソリン',
                '自動車税(円)': '39500', '乗車定員': '8', '中古相場(万円)': '200~280',
                'サイズ(mm)': '4685×1695×1870'
            },
            {
                'メーカー': 'スズキ', '車種': 'スペーシア', 'ボディタイプ': '軽自動車',
                '駆動方式': '2WD', '価格(万円)': '140', '排気量': '660',
                '年式': '2024', '燃費(km/L)': '22.0', '燃料の種類': 'ハイブリッド',
                '自動車税(円)': '10800', '乗車定員': '4', '中古相場(万円)': '90~140',
                'サイズ(mm)': '3395×1475×1785'
            },
            {
                'メーカー': 'BMW', '車種': 'X3', 'ボディタイプ': 'SUV',
                '駆動方式': '4WD', '価格(万円)': '680', '排気量': '2000',
                '年式': '2024', '燃費(km/L)': '14.0', '燃料の種類': 'ガソリン',
                '自動車税(円)': '45000', '乗車定員': '5', '中古相場(万円)': '400~600',
                'サイズ(mm)': '4720×1890×1680'
            }
        ]
        
        # 指定された数だけデータを追加
        for i, car_data in enumerate(demo_cars[:limit]):
            car_info = car_data.copy()
            car_info['id'] = len(self.data) + 1
            car_info['モデル'] = ''
            car_info['安全評価'] = '5'
            
            # DataFrameに追加
            self.data = pd.concat([self.data, pd.DataFrame([car_info])], ignore_index=True)
            print(f"✓ デモデータ追加完了 ({i+1}/{limit}): {car_info['メーカー']} {car_info['車種']}")
        
        print(f"デモデータ生成完了！生成した車両数: {len(self.data)}")
        
        # CSVに保存
        self.save_to_csv()

    def scrape_goo_net(self, limit=10):
        """
        Goo-netから車両情報をスクレイピングする
        注意: 実際のスクレイピング実装には利用規約の確認と適切な間隔での実行が必要

        Parameters:
        -----------
        limit : int
            スクレイピングする車両数の上限
        """
        print(f"Goo-netからの車両情報スクレイピングは現在テスト段階です。")
        print(f"代わりにデモデータを生成します...")
        
        # 実際のスクレイピングは利用規約の確認が必要なため、デモデータで代替
        self.scrape_simple_demo_data(limit)

    def _extract_car_info(self, soup, maker, car_name):
        """
        車両詳細ページから情報を抽出する (Goo-net用)
        
        Parameters:
        -----------
        soup : BeautifulSoup
            車両詳細ページのBeautifulSoupオブジェクト
        maker : str
            メーカー名
        car_name : str
            車種名
            
        Returns:
        --------
        dict
            抽出した車両情報
        """
        car_info = {
            'id': len(self.data) + 1,
            'メーカー': maker,
            '車種': car_name,
            'ボディタイプ': '',
            '駆動方式': '',
            '価格(万円)': '',
            '排気量': '',
            '年式': '',
            'モデル': '',
            '安全評価': '',
            '燃費(km/L)': '',
            '燃料の種類': '',
            '自動車税(円)': '',
            '乗車定員': '',
            '中古相場(万円)': '',
            'サイズ(mm)': ''
        }

        try:
            # 詳細テーブルから各項目を取得
            spec_table = soup.select_one('table.specTable')
            if spec_table:
                rows = spec_table.select('tr')
                for row in rows:
                    header = row.select_one('th')
                    value = row.select_one('td')
                    
                    if header and value:
                        header_text = header.text.strip()
                        value_text = value.text.strip()
                        
                        # 各項目をマッピング
                        if '価格' in header_text:
                            price_match = re.search(r'(\d+\.?\d*)万円', value_text)
                            if price_match:
                                car_info['価格(万円)'] = price_match.group(1)
                        
                        elif 'ボディタイプ' in header_text:
                            car_info['ボディタイプ'] = value_text
                        
                        elif '駆動方式' in header_text:
                            car_info['駆動方式'] = value_text
                        
                        elif '排気量' in header_text:
                            car_info['排気量'] = value_text
                        
                        elif '燃費' in header_text:
                            fuel_match = re.search(r'(\d+\.?\d*)km/L', value_text)
                            if fuel_match:
                                car_info['燃費(km/L)'] = fuel_match.group(1)
                        
                        elif '燃料' in header_text:
                            car_info['燃料の種類'] = value_text
                        
                        elif '年式' in header_text:
                            car_info['年式'] = value_text
                        
                        elif '乗車定員' in header_text:
                            seats_match = re.search(r'(\d+)人', value_text)
                            if seats_match:
                                car_info['乗車定員'] = seats_match.group(1)
                        
                        elif 'サイズ' in header_text or '全長' in header_text:
                            length = re.search(r'全長[：:]?\s*(\d+)mm', value_text)
                            width = re.search(r'全幅[：:]?\s*(\d+)mm', value_text)
                            height = re.search(r'全高[：:]?\s*(\d+)mm', value_text)
                            
                            if length and width and height:
                                car_info['サイズ(mm)'] = f"{length.group(1)}×{width.group(1)}×{height.group(1)}"

            # 中古相場情報を取得
            used_price_elem = soup.select_one('div.usedPriceArea')
            if used_price_elem:
                price_text = used_price_elem.text
                price_range = re.search(r'(\d+)万円[～~](\d+)万円', price_text)
                if price_range:
                    car_info['中古相場(万円)'] = f"{price_range.group(1)}~{price_range.group(2)}"
            
        except Exception as e:
            print(f"    情報抽出中にエラー: {e}")
        
        return car_info

    def merge_with_existing_csv(self, existing_csv_path="car_data.csv"):
        """
        既存のCSVファイルとスクレイピング結果をマージする
        
        Parameters:
        -----------
        existing_csv_path : str
            既存のCSVファイルパス
        """
        try:
            # 既存のCSVを読み込む
            if not os.path.exists(existing_csv_path):
                print(f"既存のCSVファイル {existing_csv_path} が見つかりません。新規作成します。")
                self.save_to_csv()
                return
                
            try:
                existing_df = pd.read_csv(existing_csv_path, encoding="utf-8")
            except:
                try:
                    existing_df = pd.read_csv(existing_csv_path, encoding="shift-jis")
                except:
                    existing_df = pd.read_csv(existing_csv_path, encoding="cp932")
            
            # カラム名を統一
            expected_columns = [
                'id', 'メーカー', '車種', 'ボディタイプ', '駆動方式', '価格(万円)', 
                '排気量', '年式', 'モデル', '安全評価', '燃費(km/L)', '燃料の種類', 
                '自動車税(円)', '乗車定員', '中古相場(万円)', 'サイズ(mm)'
            ]
            
            # 既存データのカラム数を確認
            if len(existing_df.columns) == len(expected_columns):
                existing_df.columns = expected_columns
            else:
                print(f"警告: 既存CSVのカラム数が期待値と異なります。")
                print(f"期待: {len(expected_columns)}, 実際: {len(existing_df.columns)}")
            
            # 重複を避けるため、メーカーと車種で結合
            merged_df = pd.concat([existing_df, self.data], ignore_index=True)
            merged_df = merged_df.drop_duplicates(subset=['メーカー', '車種'], keep='last')
            
            # IDを振り直す
            merged_df['id'] = range(1, len(merged_df) + 1)
            
            # マージ結果を保存
            merged_df.to_csv(existing_csv_path, index=False, encoding="utf-8")
            
            print(f"既存のCSVとマージしました。合計車両数: {len(merged_df)}")
            
        except Exception as e:
            print(f"マージ処理中にエラーが発生しました: {e}")
            print("マージをスキップし、新規データのみ保存します。")
            self.save_to_csv()
    
    def save_to_csv(self):
        """スクレイピング結果をCSVファイルに保存する"""
        try:
            self.data.to_csv(self.output_path, index=False, encoding="utf-8")
            print(f"CSVファイルを保存しました: {self.output_path}")
        except Exception as e:
            print(f"CSVファイルの保存中にエラーが発生しました: {e}")

# データクリーニング関数群
def clean_price_data(price_str):
    """価格データをクリーニングする"""
    if pd.isna(price_str) or price_str == '':
        return None
    
    # 数字のみを抽出
    price_match = re.search(r'(\d+\.?\d*)', str(price_str))
    if price_match:
        return float(price_match.group(1))
    return None

def clean_fuel_economy_data(fuel_str):
    """燃費データをクリーニングする"""
    if pd.isna(fuel_str) or fuel_str == '':
        return None
    
    # km/L形式から数字を抽出
    fuel_match = re.search(r'(\d+\.?\d*)', str(fuel_str))
    if fuel_match:
        return float(fuel_match.group(1))
    return None

def clean_size_data(size_str):
    """サイズデータをクリーニングする"""
    if pd.isna(size_str) or size_str == '':
        return None
    
    # "長さ×幅×高さ"形式を標準化
    size_match = re.search(r'(\d+)[×x](\d+)[×x](\d+)', str(size_str))
    if size_match:
        return f"{size_match.group(1)}×{size_match.group(2)}×{size_match.group(3)}"
    return str(size_str)

# スクリプトとして実行する場合
if __name__ == "__main__":
    print("車両データスクレイピングツールを開始します...")
    
    scraper = CarScraper(output_path="data/raw_data.csv")
    
    # デモデータを生成（実際のスクレイピングの代替）
    scraper.scrape_simple_demo_data(limit=5)
    
    # 既存のCSVとマージ
    scraper.merge_with_existing_csv(existing_csv_path="car_data.csv")
    
    print("処理が完了しました。")