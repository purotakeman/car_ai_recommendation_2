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
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebkit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 
        }
        # 結果を保存するデータフレーム
        self.data = pd.DaraFrame(columns=[
            'id', 'メーカー', '車種', 'ボディタイプ', '駆動方式', '価格(万円)', 
            '排気量', '年式', 'モデル', '安全評価', '燃費(km/L)', '燃料の種類', 
            '自動車税(円)', '乗車定員', '中古相場(万円)', 'サイズ(mm)'
        ])

        # フォルダがなければ作成
        os.makedirs(os.path.diename(output_path), exist_ok=True)

    def scrape_goo_net(self, limit=10):
        """
        Goo-netから車両情報をスクレイピングする

        Parameters:
        -----------
        limit : int
            スクレイピングする車両数の上限
        """
        print(f"Goo-netから車両情報をスクレイピングします(最大{limit}件)...")

        # メーカーリストのURLとページ
        maker_url = "https://www.goo-net.com/catalog/"

        try:
            # メーカーページを取得
            response = requests.get(maker_url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # メーカーリンクを取得
            maker_links = soup.select('ul.makerList li a')

            car_count = 0

            # メーカー毎に処理
            for maker_link in maker_links:
                if car_count >= limit:
                    break

                maker_mame = maker_link.text.strip()
                maker_href = maker_link['href']

                print(f"メーカー: {maker_name} の情報を取得中...")

                # ランダムな待機時間(サーバー負荷軽減)
                time.sleep(random.uniform(1,3))

                # メーカーページを取得
                maker_response = requests.get("https://www.goo-net.com" + maker_href, headers=self.headers)
                maker_response.raise_for_status()

                maker_soup =  BeautifulSoup(maker_response.content, 'html.parser')

                # 車種リンクを取得
                car_links = maker_soup.select('div.carNameArea h3 a')

                # 車種毎に処理
                for car_link in car_links:
                    if car_count >= limit:
                        break

                    car_name = car_link.text.strip()
                    car_href = car_link['href']

                    print(f"  車種:{car_name} の情報を取得中...")

                    # ランダムな待機時間
                    time.sleep(random.uniform(1, 3))

                    try:
                        # 車種詳細ページを取得
                        car_response = requests.get("https://goo-net.com" + car_href, headers=self.headers)
                        car_response.raise_for_status()

                        car_soup = BeautifulSoup(car_response.content, 'html.parser')

                        # 詳細情報を抽出
                        car_info = self._exract_car_info(car_soup, maker_name, car_name)

                        # データーフレームに追加
                        self.data = pd.concat([self.data, pd.DataFrame([car_info])], ignore_index=True)

                        car_count += 1
                        print(f"   ✓情報取得完了({car_count}/{limit})")
                    
                    except Exception as e:
                        print(f"    ✗ 車種情報の取得に失敗: {e}")

                print(f"スクレイピング完了！取得した車両数: {car_count}")

                # CSVに保存
                self.save_to_csv()

        except Exception as e:
            print(f"スクレイピング中にエラーが発生しました: {e}")

    def scrape_carview(self, limit=10):
        """
        carviewから車両情報をスクレイピングする

        Parameters:
        -----------
        limit : int
            スクレイピングする車両数の上限
        """
        print(f"carviewから車両情報をスクレイピングします(最大{limit}件)...")

        # メーカーリストのURL
        maker_url = "https://carview.yahoo.co.jp/car/newcar/"

        try:
            # メーカーページを取得
            response = requests.get(maker_url, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            car_count = 0

            # メーカー毎に処理
            for maker_link in maker_links:
                if car_count >= limit:
                    break

                maker_name = maker_link.text.strip()
                maker_href = maker_link['href']

                print(f"メーカー: {maker_name} の情報を取得中...")

                # ランダムな待機時間(サーバー負荷軽減)
                time.sleep(random.uniform(1, 3))

                # メーカーページを取得
                maker_response = requests.get("https://carview.yahoo.co.jp" + maker_href, headers=self.headers)
                maker_response.raise_for_status()

                maker_soup = BeautifulSoup(maker_response.content, 'html.parser')

                # 車種リンクを取得(実際のセレクタに合わせて調子が必要)
                car_links = maker_soup.select('div.car-name a')

                # 車種ごとに処理
                for car_link in car_links:
                    if car_count >= limit:
                        break
                        
                    car_name = car_link.text.strip()
                    car_href = car_link['href']
                    
                    print(f"  車種: {car_name} の情報を取得中...")
                    
                    # ランダムな待機時間
                    time.sleep(random.uniform(1, 3))

                    try:
                        # 車種詳細ページを取得
                        car_response = requests.get("https://carview.yahoo.co.jp" + car_href, headers=self.headers)
                        car_response.raise_for_status()
                        
                        car_soup = BeautifulSoup(car_response.content, 'html.parser')
                        
                        # 詳細情報を抽出
                        car_info = self._extract_carview_info(car_soup, maker_name, car_name)
                        
                        # データフレームに追加
                        self.data = pd.concat([self.data, pd.DataFrame([car_info])], ignore_index=True)
                        
                        car_count += 1
                        print(f"    ✓ 情報取得完了 ({car_count}/{limit})")
                        
                    except Exception as e:
                        print(f"    ✗ 車種情報の取得に失敗: {e}")
            
            print(f"スクレイピング完了！取得した車両数: {car_count}")
            
            # CSVに保存
            self.save_to_csv()
            
        except Exception as e:
            print(f"スクレイピング中にエラーが発生しました: {e}")


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
                            # 価格から数字のみを抽出
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
                            # 燃費から数字のみを抽出
                            fuel_match = re.search(r'(\d+\.?\d*)km/L', value_text)
                            if fuel_match:
                                car_info['燃費(km/L)'] = fuel_match.group(1)
                        
                        elif '燃料' in header_text:
                            car_info['燃料の種類'] = value_text
                        
                        elif '年式' in header_text:
                            car_info['年式'] = value_text
                        
                        elif '乗車定員' in header_text:
                            # 乗車定員から数字のみを抽出
                            seats_match = re.search(r'(\d+)人', value_text)
                            if seats_match:
                                car_info['乗車定員'] = seats_match.group(1)
                        
                        elif 'サイズ' in header_text or '全長' in header_text:
                            # 全長×全幅×全高の形式に整形
                            length = re.search(r'全長[：:]?\s*(\d+)mm', value_text)
                            width = re.search(r'全幅[：:]?\s*(\d+)mm', value_text)
                            height = re.search(r'全高[：:]?\s*(\d+)mm', value_text)
                            
                            if length and width and height:
                                car_info['サイズ(mm)'] = f"{length.group(1)}×{width.group(1)}×{height.group(1)}"

                # 中古相場情報を取得（仮実装、実際のサイトに合わせて調整が必要）
            used_price_elem = soup.select_one('div.usedPriceArea')
            if used_price_elem:
                price_text = used_price_elem.text
                price_range = re.search(r'(\d+)万円[～~](\d+)万円', price_text)
                if price_range:
                    car_info['中古相場(万円)'] = f"{price_range.group(1)}~{price_range.group(2)}"
            
        except Exception as e:
            print(f"    情報抽出中にエラー: {e}")
        
        return car_info

    def _extract_carview_info(self, soup, maker, car_name):
        """
        車両詳細ページから情報を抽出する (carview用)
        
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
        # 基本的なGoo-netと同じ構造で、セレクタを調整
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
            # carview用のセレクタに変更
            # 仮実装として、実際のサイト構造に合わせて調整が必要
            spec_items = soup.select('dl.spec-item')
            for item in spec_items:
                header = item.select_one('dt')
                value = item.select_one('dd')
                
                if header and value:
                    header_text = header.text.strip()
                    value_text = value.text.strip()
                    
                    # 各項目をマッピング (carview用に調整)
                    if '価格' in header_text:
                        price_match = re.search(r'(\d+\.?\d*)万円', value_text)
                        if price_match:
                            car_info['価格(万円)'] = price_match.group(1)
                    
                    elif 'ボディタイプ' in header_text:
                        car_info['ボディタイプ'] = value_text
                    
                    elif '駆動方式' in header_text:
                        car_info['駆動方式'] = value_text
                    
                    # 他の項目も同様に抽出
                    
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
            try:
                existing_df = pd.read_csv(existing_csv_path, encoding="utf-8")
            except:
                try:
                    existing_df = pd.read_csv(existing_csv_path, encoding="shift-jis")
                except:
                    existing_df = pd.read_csv(existing_csv_path, encoding="cp932")
            
            # カラム名を統一
            existing_df.columns = [
                'id', 'メーカー', '車種', 'ボディタイプ', '駆動方式', '価格(万円)', 
                '排気量', '年式', 'モデル', '安全評価', '燃費(km/L)', '燃料の種類', 
                '自動車税(円)', '乗車定員', '中古相場(万円)', 'サイズ(mm)'
            ]
            
            # 重複を避けるため、メーカーと車種で結合
            merged_df = pd.concat([existing_df, self.data])
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

# スクリプトとして実行する場合
if __name__ == "__main__":
    scraper = CarScraper(output_path="data/raw_data.csv")
    
    # Goo-netから10台の車両情報をスクレイピング
    scraper.scrape_goo_net(limit=10)
    
    # 既存のCSVとマージ
    scraper.merge_with_existing_csv(existing_csv_path="car_data.csv")