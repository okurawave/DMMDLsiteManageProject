#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import logging
import urllib.parse
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from bs4 import BeautifulSoup
from .scraper_base import ScraperBase

logger = logging.getLogger(__name__)

class DlsiteScraper(ScraperBase):
    """
    DLsiteサイトから商品情報をスクレイピングするクラス
    """
    
    BASE_URL = "https://www.dlsite.com"
    SEARCH_URL = "https://www.dlsite.com/maniax/fsr/=/language/jp/keyword/{}/age_category%5B0%5D/general/"
    PRODUCT_URL = "https://www.dlsite.com/maniax/work/=/product_id/{}"
    
    def __init__(self, delay: float = 1.5, timeout: int = 15, max_retries: int = 3):
        """
        Parameters
        ----------
        delay: float
            リクエスト間の遅延（秒）
        timeout: int
            リクエストのタイムアウト（秒）
        max_retries: int
            リクエストの最大リトライ回数
        """
        super().__init__(delay=delay, timeout=timeout, max_retries=max_retries)
    
    def search_products(self, keyword: str, max_items: int = 20) -> List[Dict[str, Any]]:
        """
        キーワードでDLsiteの商品を検索する
        
        Parameters
        ----------
        keyword: str
            検索キーワード
        max_items: int
            取得する最大アイテム数
            
        Returns
        -------
        List[Dict[str, Any]]
            検索結果の商品リスト
        """
        logger.info(f"DLsiteで検索: キーワード '{keyword}', 最大アイテム数 {max_items}")
        
        # URLエンコード
        encoded_keyword = urllib.parse.quote(keyword)
        search_url = self.SEARCH_URL.format(encoded_keyword)
        
        results = []
        page_num = 1
        
        # 検索結果ページを解析
        while len(results) < max_items:
            # ページネーションに対応（必要に応じてURLを調整）
            page_url = search_url
            if page_num > 1:
                page_url += f"&page={page_num}"
            
            soup = self._get_page(page_url)
            items = self._parse_search_results(soup)
            
            if not items:
                # これ以上アイテムがなければ終了
                logger.info(f"検索結果がこれ以上ありません。ページ {page_num}")
                break
                
            results.extend(items[:max_items - len(results)])
            
            if len(items) < 20:  # 1ページの最大表示数より少なければ次のページはない
                break
                
            page_num += 1
            
        logger.info(f"DLsiteで {len(results)} アイテムを取得しました")
        return results[:max_items]
    
    def _parse_search_results(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        検索結果ページから商品情報を抽出する
        
        Parameters
        ----------
        soup: BeautifulSoup
            検索結果ページのBeautifulSoupオブジェクト
            
        Returns
        -------
        List[Dict[str, Any]]
            解析された商品リスト
        """
        items = []
        try:
            # DLsite検索結果の商品要素を抽出
            # 注: このセレクタはDLsiteサイトの構造変更に応じて更新が必要
            product_elements = soup.select('.n_worklist_item')
            
            for element in product_elements:
                try:
                    # 商品IDを抽出
                    product_id = None
                    for class_name in element.get('class', []):
                        if class_name.startswith('_'):
                            product_id = class_name[1:]  # '_RJ123456' から 'RJ123456' を抽出
                            break
                    
                    if not product_id:
                        continue
                    
                    # 商品URLを生成
                    url = self.PRODUCT_URL.format(product_id)
                    
                    # タイトルを抽出
                    title_element = element.select_one('.work_name a')
                    title = title_element.get_text(strip=True) if title_element else "タイトル不明"
                    
                    # サムネイル画像を抽出
                    img_element = element.select_one('.work_thumb img')
                    thumbnail_url = None
                    if img_element:
                        thumbnail_url = img_element.get('src') or img_element.get('data-src')
                    
                    # 価格を抽出
                    price_element = element.select_one('.work_price')
                    price_text = price_element.get_text(strip=True) if price_element else None
                    price = self.normalize_price(price_text)
                    
                    # セール価格を抽出
                    discount_price = None
                    discount_element = element.select_one('.work_price.discount')
                    if discount_element:
                        original_price_element = element.select_one('.work_price.strike')
                        if original_price_element:
                            original_price_text = original_price_element.get_text(strip=True)
                            original_price = self.normalize_price(original_price_text)
                            # セール中の場合、通常価格とセール価格を設定
                            discount_price = price
                            price = original_price
                    
                    # メーカー/サークル名を抽出
                    maker_element = element.select_one('.maker_name a')
                    maker = maker_element.get_text(strip=True) if maker_element else None
                    
                    items.append({
                        'platform': 'dlsite',
                        'platform_id': product_id,
                        'title': title,
                        'url': url,
                        'thumbnail_url': thumbnail_url,
                        'price': price,
                        'discount_price': discount_price,
                        'maker': maker
                    })
                    
                except Exception as e:
                    logger.error(f"商品要素の解析中にエラーが発生しました: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"検索結果の解析中にエラーが発生しました: {str(e)}")
        
        return items
    
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        DLsiteの商品詳細情報を取得する
        
        Parameters
        ----------
        product_id: str
            商品ID（例：RJ123456）
            
        Returns
        -------
        Dict[str, Any]
            商品の詳細情報
        """
        logger.info(f"DLsiteの商品詳細を取得: 商品ID '{product_id}'")
        
        url = self.PRODUCT_URL.format(product_id)
        soup = self._get_page(url)
        
        details = {
            'platform': 'dlsite',
            'platform_id': product_id,
            'url': url
        }
        
        try:
            # タイトルの取得
            title_element = soup.select_one('#work_name')
            if title_element:
                details['title'] = title_element.get_text(strip=True)
            
            # 画像URLの取得
            img_element = soup.select_one('.product-slider-data img')
            if img_element and (img_src := img_element.get('src') or img_element.get('data-src')):
                details['thumbnail_url'] = img_src
                
            # 価格情報の取得
            price_element = soup.select_one('.work_price')
            if price_element:
                price_text = price_element.get_text(strip=True)
                details['price'] = self.normalize_price(price_text)
                
            # セール価格の取得
            discount_element = soup.select_one('.work_price.discount')
            if discount_element:
                discount_price_text = discount_element.get_text(strip=True)
                original_price_element = soup.select_one('.work_price.strike')
                if original_price_element:
                    original_price_text = original_price_element.get_text(strip=True)
                    details['price'] = self.normalize_price(original_price_text)
                    details['discount_price'] = self.normalize_price(discount_price_text)
                    
            # メーカー/サークル名の取得
            maker_element = soup.select_one('.maker_name a')
            if maker_element:
                details['maker'] = maker_element.get_text(strip=True)
                
            # 発売日の取得
            # DLsiteの発売日表記例：「販売日：2023年01月01日」
            date_element = soup.select_one('#work_outline tr:contains("販売日") td')
            if date_element:
                date_text = date_element.get_text(strip=True)
                date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', date_text)
                if date_match:
                    year = int(date_match.group(1))
                    month = int(date_match.group(2))
                    day = int(date_match.group(3))
                    details['release_date'] = datetime(year, month, day).date().isoformat()
            
            # カテゴリの取得
            category_elements = soup.select('#work_outline tr:contains("ジャンル") td a')
            if category_elements:
                details['category'] = [elem.get_text(strip=True) for elem in category_elements]
            
            # ファイル形式の取得
            file_type_element = soup.select_one('#work_outline tr:contains("ファイル形式") td')
            if file_type_element:
                details['file_type'] = file_type_element.get_text(strip=True)
                
            # ファイルサイズの取得
            file_size_element = soup.select_one('#work_outline tr:contains("ファイル容量") td')
            if file_size_element:
                details['file_size'] = file_size_element.get_text(strip=True)
            
        except Exception as e:
            logger.error(f"商品詳細の解析中にエラーが発生しました: {str(e)}")
        
        return details