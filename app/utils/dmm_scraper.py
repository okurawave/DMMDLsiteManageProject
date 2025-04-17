#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from app.utils.scraper_base import ScraperBase

logger = logging.getLogger(__name__)

class DmmScraper(ScraperBase):
    """DMM.comのスクレイピングを行うクラス"""
    
    LOGIN_URL = "https://accounts.dmm.co.jp/service/login/password"
    PURCHASE_HISTORY_URL = "https://www.dmm.co.jp/digital/-/purchases/"
    SEARCH_URL = "https://www.dmm.co.jp/digital/videoa/-/list/search/=/?searchstr={keyword}"
    PRODUCT_URL = "https://www.dmm.co.jp/digital/videoa/-/detail/=/cid={product_id}/"
    
    async def authenticate(self, username, password):
        """DMMへのログイン処理"""
        try:
            # ログインページに移動
            await self.page.goto(self.LOGIN_URL)
            
            # ユーザー名とパスワードを入力
            await self.page.fill('input[id="login_id"]', username)
            await self.page.fill('input[id="password"]', password)
            
            # ログインボタンをクリック
            await self.page.click('button[type="submit"]')
            
            # ログイン後のリダイレクトを待つ
            await self.page.wait_for_load_state('networkidle')
            
            # ログインの成功を確認（マイページへのリンクがあるか）
            my_page_link = await self.page.query_selector('a:text("DMMアカウント")')
            
            if my_page_link:
                logger.info("DMMへのログインに成功しました")
                return True
            else:
                logger.warning("DMMへのログインに失敗しました")
                return False
                
        except Exception as e:
            logger.error(f"認証中にエラーが発生しました: {e}")
            return False
    
    async def search_products(self, keyword, max_items=10):
        """キーワードによる商品検索"""
        results = []
        try:
            search_url = self.SEARCH_URL.format(keyword=keyword)
            await self.page.goto(search_url)
            await self.page.wait_for_load_state('networkidle')
            
            # 検索結果の商品要素を取得
            items = await self.page.query_selector_all('.productList .tmb')
            
            count = 0
            for item in items:
                if count >= max_items:
                    break
                
                try:
                    # 商品情報を抽出
                    title_element = await item.query_selector('a img')
                    title = await title_element.get_attribute('alt') if title_element else "不明"
                    
                    link_element = await item.query_selector('a')
                    url = await link_element.get_attribute('href') if link_element else ""
                    
                    # URLから商品IDを抽出
                    platform_id = None
                    if url:
                        match = re.search(r'cid=([^/&]+)', url)
                        if match:
                            platform_id = match.group(1)
                    
                    # 価格情報を取得
                    price_element = await item.query_selector('//parent::li//p[contains(@class, "price")]')
                    price_text = await price_element.inner_text() if price_element else ""
                    price = None
                    if price_text:
                        price_match = re.search(r'¥([\d,]+)', price_text)
                        if price_match:
                            price = int(price_match.group(1).replace(',', ''))
                    
                    # サムネイル画像
                    thumbnail_url = await title_element.get_attribute('src') if title_element else None
                    
                    # メーカー情報を取得（商品詳細ページからの取得が必要かもしれない）
                    maker = "不明"  # 一覧ページではメーカー情報が取得しにくい場合あり
                    
                    if platform_id:
                        product_data = {
                            'platform': 'dmm',
                            'platform_id': platform_id,
                            'title': title,
                            'maker': maker,
                            'price': price,
                            'url': url,
                            'thumbnail_url': thumbnail_url
                        }
                        results.append(product_data)
                        count += 1
                
                except Exception as e:
                    logger.error(f"商品情報の抽出中にエラーが発生しました: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"商品検索中にエラーが発生しました: {e}")
            return []
    
    async def get_product_details(self, product_id):
        """商品詳細情報の取得"""
        try:
            product_url = self.PRODUCT_URL.format(product_id=product_id)
            await self.page.goto(product_url)
            await self.page.wait_for_load_state('networkidle')
            
            # タイトル
            title_element = await self.page.query_selector('h1#title')
            title = await title_element.inner_text() if title_element else "不明"
            
            # メーカー
            maker_element = await self.page.query_selector('span[data-type="maker"] a')
            maker = await maker_element.inner_text() if maker_element else "不明"
            
            # 価格
            price_element = await self.page.query_selector('.priceList__main .priceList__txt')
            price_text = await price_element.inner_text() if price_element else ""
            price = None
            if price_text:
                price_match = re.search(r'¥([\d,]+)', price_text)
                if price_match:
                    price = int(price_match.group(1).replace(',', ''))
            
            # サムネイル画像
            thumbnail_element = await self.page.query_selector('meta[property="og:image"]')
            thumbnail_url = await thumbnail_element.get_attribute('content') if thumbnail_element else None
            
            # 発売日
            release_element = await self.page.query_selector('tr:has(td:text-is("配信開始日")) td:nth-child(2)')
            release_date_text = await release_element.inner_text() if release_element else ""
            release_date = None
            if release_date_text:
                try:
                    release_date = datetime.strptime(release_date_text, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                except:
                    pass
            
            # 商品情報をまとめる
            product_data = {
                'platform': 'dmm',
                'platform_id': product_id,
                'title': title,
                'maker': maker,
                'price': price,
                'url': product_url,
                'thumbnail_url': thumbnail_url,
                'release_date': release_date
            }
            
            return product_data
            
        except Exception as e:
            logger.error(f"商品詳細の取得中にエラーが発生しました: {e}")
            return None
    
    async def get_purchase_history(self, start_date=None, end_date=None, max_pages=1):
        """購入履歴の取得"""
        purchase_history = []
        
        try:
            # 購入履歴ページに移動
            await self.page.goto(self.PURCHASE_HISTORY_URL)
            await self.page.wait_for_load_state('networkidle')
            
            # ログイン状態の確認
            if "login" in self.page.url:
                logger.error("DMM: ログインが必要です")
                return []
            
            page_count = 0
            has_next = True
            
            while has_next and page_count < max_pages:
                # 購入履歴テーブルの各行を取得
                items = await self.page.query_selector_all('table.purchase-history tr:not(:first-child)')
                
                for item in items:
                    try:
                        # 購入日
                        date_element = await item.query_selector('td:nth-child(1)')
                        purchase_date_text = await date_element.inner_text() if date_element else ""
                        purchase_date = None
                        if purchase_date_text:
                            purchase_date = datetime.strptime(purchase_date_text, '%Y年%m月%d日').strftime('%Y-%m-%d')
                        
                        # 日付範囲でフィルタリング
                        if start_date and purchase_date and purchase_date < start_date:
                            continue
                        if end_date and purchase_date and purchase_date > end_date:
                            continue
                        
                        # タイトル
                        title_element = await item.query_selector('td:nth-child(2) p.title a')
                        title = await title_element.inner_text() if title_element else "不明"
                        
                        # URL
                        url = await title_element.get_attribute('href') if title_element else ""
                        
                        # プラットフォームID抽出
                        platform_id = None
                        if url:
                            match = re.search(r'cid=([^/&]+)', url)
                            if match:
                                platform_id = match.group(1)
                        
                        # 価格
                        price_element = await item.query_selector('td:nth-child(4)')
                        price_text = await price_element.inner_text() if price_element else ""
                        price = None
                        if price_text:
                            price_match = re.search(r'¥([\d,]+)', price_text)
                            if price_match:
                                price = int(price_match.group(1).replace(',', ''))
                        
                        # メーカー
                        maker_element = await item.query_selector('td:nth-child(2) p.maker a')
                        maker = await maker_element.inner_text() if maker_element else "不明"
                        
                        if platform_id:
                            purchase_data = {
                                'platform': 'dmm',
                                'platform_id': platform_id,
                                'title': title,
                                'maker': maker,
                                'price': price,
                                'url': url,
                                'purchase_date': purchase_date
                            }
                            purchase_history.append(purchase_data)
                    
                    except Exception as e:
                        logger.error(f"購入履歴の抽出中にエラーが発生しました: {e}")
                        continue
                
                # 次のページがあるか確認
                next_button = await self.page.query_selector('li.area-pagination-next:not(.is-disabled) a')
                if next_button and page_count < max_pages - 1:
                    await next_button.click()
                    await self.page.wait_for_load_state('networkidle')
                    page_count += 1
                else:
                    has_next = False
            
            return purchase_history
            
        except Exception as e:
            logger.error(f"購入履歴の取得中にエラーが発生しました: {e}")
            return []