# -*- coding: utf-8 -*-
"""
車両データ収集・拡張スクリプト
BeautifulSoupを使用したWebスクレイピング機能

使用方法:
1. 基本実行: python car_scraper.py
2. デモデータ生成: python car_scraper.py --demo
3. 既存データと結合: python car_scraper.py --merge
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import os
import re
import sys
import argparse
from datetime import datetime


class CarDataEnhancer:
    def __init__(self, output_path="../data/raw_data.csv"):
        """
        車両データ拡張クラス

        parameters:
        -----------
        output_path : str
            出力csvファイルのパス
        """
        self.output_path = output_path
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        # 結果を保存するデータフレーム
        # 修正: DataFrameのスペルミス修正
        self.data = pd.DataFrame(columns=[
            'id', 'メーカー', '車種', 'ボディタイプ', '駆動方式', '価格(万円)', 
            '排気量', '年式', 'モデル', '安全評価', '燃費(km/L)', '燃料の種類', 
            '自動車税(円)', '乗車定員', '中古相場(万円)', 'サイズ(mm)'
        ])

        # ディレクトリが存在しない場合は作成
        # 修正: Trueの大文字小文字修正
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

    def generate_enhanced_demo_data(self, count=10):
        """
        拡張されたデモ用車両データを生成
        
        Parameters:
        -----------
        count : int
            生成する車両数
        """
        print(f"拡張デモ用車両データを生成します({count}件)...")

        # より充実したデモ用データセット
        demo_cars = [
            {
                'メーカー': 'トヨタ', '車種': 'アクア', 'ボディタイプ': 'ハッチバック',
                '駆動方式': '2WD', '価格(万円)': '220', '排気量': '1500',
                '年式': '2024', 'モデル': 'G', '燃費(km/L)': '35.8', '燃料の種類': 'ハイブリッド',
                '自動車税(円)': '34500', '乗車定員': '5', '中古相場(万円)': '140~180',
                'サイズ(mm)': '4050×1695×1485', '安全評価': '5'
            },
            {
                'メーカー': 'ホンダ', '車種': 'フリード', 'ボディタイプ': 'ミニバン',
                '駆動方式': '2WD', '価格(万円)': '280', '排気量': '1500',
                '年式': '2024', 'モデル': 'HYBRID G', '燃費(km/L)': '28.0', '燃料の種類': 'ハイブリッド',
                '自動車税(円)': '34500', '乗車定員': '6', '中古相場(万円)': '190~240',
                'サイズ(mm)': '4265×1695×1710', '安全評価': '5'
            },
            # 修正: カンマ追加
            {
                'メーカー': '日産', '車種': 'リーフ', 'ボディタイプ': 'ハッチバック',
                '駆動方式': '2WD', '価格(万円)': '408', '排気量': '0',
                '年式': '2024', 'モデル': 'X', '燃費(km/L)': '100.0', '燃料の種類': 'EV',
                '自動車税(円)': '29500', '乗車定員': '5', '中古相場(万円)': '200~300',
                'サイズ(mm)': '4480×1790×1565', '安全評価': '5'
            },
            {
                'メーカー': 'スバル', '車種': 'レヴォーグ', 'ボディタイプ': 'ワゴン',
                '駆動方式': '4WD', '価格(万円)': '370', '排気量': '1800',
                '年式': '2024', 'モデル': 'STI Sport', '燃費(km/L)': '16.6', '燃料の種類': 'ガソリン',
                '自動車税(円)': '39500', '乗車定員': '5', '中古相場(万円)': '250~350',
                'サイズ(mm)': '4755×1795×1500', '安全評価': '5'
            },
            {
                'メーカー': 'マツダ', '車種': 'MAZDA3', 'ボディタイプ': 'ハッチバック',
                '駆動方式': '2WD', '価格(万円)': '290', '排気量': '2000',
                '年式': '2024', 'モデル': 'X PROACTIVE', '燃費(km/L)': '19.8', '燃料の種類': 'ガソリン',
                '自動車税(円)': '39500', '乗車定員': '5', '中古相場(万円)': '180~260',
                'サイズ(mm)': '4460×1795×1440', '安全評価': '5'
            },
            {
                'メーカー': 'ダイハツ', '車種': 'ロッキー', 'ボディタイプ': 'SUV',
                '駆動方式': '2WD', '価格(万円)': '190', '排気量': '1000',
                '年式': '2024', 'モデル': 'G', '燃費(km/L)': '20.7', '燃料の種類': 'ガソリン',
                '自動車税(円)': '29500', '乗車定員': '5', '中古相場(万円)': '120~170',
                'サイズ(mm)': '3995×1695×1620', '安全評価': '4'
            },
            {
                'メーカー': 'スズキ', '車種': 'ハスラー', 'ボディタイプ': '軽自動車',
                '駆動方式': '4WD', '価格(万円)': '168', '排気量': '660',
                '年式': '2024', 'モデル': 'HYBRID G', '燃費(km/L)': '25.0', '燃料の種類': 'ハイブリッド',
                '自動車税(円)': '10800', '乗車定員': '4', '中古相場(万円)': '110~160',
                'サイズ(mm)': '3395×1475×1680', '安全評価': '4'
            },
            {
                'メーカー': '三菱', '車種': 'eKクロス', 'ボディタイプ': '軽自動車',
                '駆動方式': '2WD', '価格(万円)': '155', '排気量': '660',
                '年式': '2024', 'モデル': 'G', '燃費(km/L)': '21.2', '燃料の種類': 'ガソリン',
                '自動車税(円)': '10800', '乗車定員': '4', '中古相場(万円)': '90~140',
                'サイズ(mm)': '3395×1475×1640', '安全評価': '4'
            },
            {
                'メーカー': 'レクサス', '車種': 'UX', 'ボディタイプ': 'SUV',
                '駆動方式': '4WD', '価格(万円)': '620', '排気量': '2000',
                '年式': '2024', 'モデル': 'UX250h', '燃費(km/L)': '25.2', '燃料の種類': 'ハイブリッド',
                '自動車税(円)': '39500', '乗車定員': '5', '中古相場(万円)': '400~580',
                'サイズ(mm)': '4495×1840×1540', '安全評価': '5'
            },
            {
                'メーカー': '日産', '車種': 'キューブ', 'ボディタイプ': 'ハッチバック',
                '駆動方式': '2WD', '価格(万円)': '185', '排気量': '1500',
                '年式': '2023', 'モデル': '15X', '燃費(km/L)': '19.0', '燃料の種類': 'ガソリン',
                '自動車税(円)': '34500', '乗車定員': '5', '中古相場(万円)': '80~140',
                'サイズ(mm)': '3890×1695×1650', '安全評価': '4'
            }
        ]

        # 指定された数だけデータを追加
        for i, car_data in enumerate(demo_cars[:count]):
            car_info = car_data.copy()
            car_info['id'] = len(self.data) + 1

            # DataFrameに追加
            self.data = pd.concat([self.data, pd.DataFrame([car_info])], ignore_index=True)
            print(f"拡張デモデータ追加完了({i+1}/{count}): {car_info['メーカー']} {car_info['車種']}")

        print(f"拡張デモデータ生成完了！生成した車両数: {len(self.data)}")

        # csvに保存
        self.save_to_csv()

    def save_to_csv(self):
        """結果をCSVファイルに保存"""
        try:
            self.data.to_csv(self.output_path, index=False, encoding="utf-8")
            print(f"CSVファイルを保存しました: {self.output_path}")
        except Exception as e:
            print(f"CSVファイルの保存中にエラーが発生しました: {e}")

    # 他のメソッドは長くなるため省略...
    # （実際のファイルでは全メソッドを含める必要があります）

def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='車両データ収集・拡張ツール')
    parser.add_argument('--demo', action='store_true', help='デモデータを生成')
    parser.add_argument('--count', type=int, default=10, help='生成するデモデータ数')
    
    args = parser.parse_args()
    
    # CarDataEnhancerのインスタンス作成
    enhancer = CarDataEnhancer()
    
    if args.demo:
        # デモデータ生成
        enhancer.generate_enhanced_demo_data(args.count)
    else:
        print("車両データ収集・拡張ツール")
        print("使用方法:")
        print("  --demo: デモデータを生成")
        print("  --count N: デモデータ数を指定（デフォルト: 10）")

if __name__ == "__main__":
    main()