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

class DmmScraper(ScraperBase):
    """
    DMMサイトから商品情報をスクレイピングするクラス
    """
    
    BASE_URL = "https://www.dmm.co.jp"
    SEARCH_URL = "https://www.dmm.co.jp/search/=/searchstr={}"
    PRODUCT_URL = "https://www.dmm.co.jp/dc/doujin/-/detail/=/cid={}/"
    
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
        キーワードでDMMサイトの商品を検索する
        
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
        logger.info(f"DMMで検索: キーワード '{keyword}', 最大アイテム数 {max_items}")
        
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
            
        logger.info(f"DMMで {len(results)} アイテムを取得しました")
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
            # DMM検索結果の商品要素を抽出
            # 注: このセレクタはDMMサイトの構造変更に応じて更新が必要
            product_elements = soup.select('.productList .productWrap')
            
            for element in product_elements:
                try:
                    # 商品IDを抽出
                    link_element = element.select_one('a.productTitle')
                    if not link_element or not link_element.get('href'):
                        continue
                    
                    url = link_element['href']
                    product_id = self._extract_product_id(url)
                    if not product_id:
                        continue
                    
                    # タイトルを抽出
                    title = link_element.get_text(strip=True) if link_element else "タイトル不明"
                    
                    # サムネイル画像を抽出
                    img_element = element.select_one('img')
                    thumbnail_url = img_element['src'] if img_element and img_element.get('src') else None
                    
                    # 価格を抽出
                    price_element = element.select_one('.prices')
                    price_text = price_element.get_text(strip=True) if price_element else None
                    price = self.normalize_price(price_text)
                    
                    # メーカー/サークル名を抽出
                    maker_element = element.select_one('.circleName')
                    maker = maker_element.get_text(strip=True) if maker_element else None
                    
                    items.append({
                        'platform': 'dmm',
                        'platform_id': product_id,
                        'title': title,
                        'url': url,
                        'thumbnail_url': thumbnail_url,
                        'price': price,
                        'maker': maker
                    })
                    
                except Exception as e:
                    logger.error(f"商品要素の解析中にエラーが発生しました: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"検索結果の解析中にエラーが発生しました: {str(e)}")
        
        return items
    
    def _extract_product_id(self, url: str) -> Optional[str]:
        """
        製品URLからIDを抽出する
        
        Parameters
        ----------
        url: str
            製品URL
            
        Returns
        -------
        Optional[str]
            製品ID、抽出できない場合はNone
        """
        # 例：https://www.dmm.co.jp/dc/doujin/-/detail/=/cid=d_123456/
        match = re.search(r'cid=([^/]+)', url)
        if match:
            return match.group(1)
        return None
    
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        DMMの商品詳細情報を取得する
        
        Parameters
        ----------
        product_id: str
            商品ID（cid=の後の値）
            
        Returns
        -------
        Dict[str, Any]
            商品の詳細情報
        """
        logger.info(f"DMMの商品詳細を取得: 商品ID '{product_id}'")
        
        url = self.PRODUCT_URL.format(product_id)
        soup = self._get_page(url)
        
        details = {
            'platform': 'dmm',
            'platform_id': product_id,
            'url': url
        }
        
        try:
            # タイトルの取得
            title_element = soup.select_one('.productTitle h1')
            if title_element:
                details['title'] = title_element.get_text(strip=True)
            
            # 画像URLの取得
            img_element = soup.select_one('.productPreview img')
            if img_element and img_element.get('src'):
                details['thumbnail_url'] = img_element['src']
                
            # 価格情報の取得
            price_element = soup.select_one('.priceWrap .price')
            if price_element:
                price_text = price_element.get_text(strip=True)
                details['price'] = self.normalize_price(price_text)
                
            # 通常価格と割引価格の取得
            discount_element = soup.select_one('.priceWrap .discount')
            if discount_element:
                regular_price_text = discount_element.get_text(strip=True)
                details['regular_price'] = self.normalize_price(regular_price_text)
                details['discount_price'] = details.get('price')
            
            # メーカー/サークル名の取得
            maker_element = soup.select_one('.circleName a')
            if maker_element:
                details['maker'] = maker_element.get_text(strip=True)
                
            # 発売日の取得
            release_element = soup.select_one('.releaseDate')
            if release_element:
                release_text = release_element.get_text(strip=True).replace('発売日：', '')
                try:
                    details['release_date'] = datetime.strptime(release_text, '%Y-%m-%d').date().isoformat()
                except ValueError:
                    pass
            
            # カテゴリの取得
            category_element = soup.select_one('.productInfo tr:contains("ジャンル") td')
            if category_element:
                details['category'] = category_element.get_text(strip=True)
                
            # 販売状況の取得
            status_element = soup.select_one('.productInfo tr:contains("販売状況") td')
            if status_element:
                details['status'] = status_element.get_text(strip=True)
            
        except Exception as e:
            logger.error(f"商品詳細の解析中にエラーが発生しました: {str(e)}")
        
        return details