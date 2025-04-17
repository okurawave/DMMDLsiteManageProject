#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
from abc import ABC, abstractmethod
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ScraperBase(ABC):
    """スクレイパーの基底クラス"""
    
    def __init__(self):
        self.authenticated = False
        self.browser = None
        self.context = None
        self.page = None
    
    async def initialize_browser(self, headless=True):
        """Playwrightブラウザを初期化する"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=headless)
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
            )
            self.page = await self.context.new_page()
            # ダウンロードを待つための設定
            await self.page.set_default_timeout(30000)  # タイムアウトを30秒に設定
            return True
        except Exception as e:
            logger.error(f"ブラウザの初期化中にエラーが発生しました: {e}")
            return False
    
    async def close_browser(self):
        """ブラウザを閉じる"""
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
                self.context = None
                self.page = None
        except Exception as e:
            logger.error(f"ブラウザの終了中にエラーが発生しました: {e}")
    
    @abstractmethod
    async def authenticate(self, username, password):
        """認証（ログイン）処理"""
        pass
    
    @abstractmethod
    async def search_products(self, keyword, max_items=10):
        """商品検索"""
        pass
    
    @abstractmethod
    async def get_product_details(self, product_id):
        """商品詳細取得"""
        pass
    
    @abstractmethod
    async def get_purchase_history(self, start_date=None, end_date=None, max_pages=1):
        """購入履歴取得"""
        pass
    
    def run_async(self, coro):
        """非同期関数を同期的に実行するためのヘルパーメソッド"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)
    
    # 同期的なインターフェースを提供するためのラッパーメソッド
    def authenticate(self, username, password):
        """認証（ログイン）処理の同期ラッパー"""
        return self.run_async(self._authenticate(username, password))
    
    def search_products(self, keyword, max_items=10):
        """商品検索の同期ラッパー"""
        return self.run_async(self._search_products(keyword, max_items))
    
    def get_product_details(self, product_id):
        """商品詳細取得の同期ラッパー"""
        return self.run_async(self._get_product_details(product_id))
    
    def get_purchase_history(self, start_date=None, end_date=None, max_pages=1):
        """購入履歴取得の同期ラッパー"""
        return self.run_async(self._get_purchase_history(start_date, end_date, max_pages))
    
    # 非同期メソッドの実装
    async def _authenticate(self, username, password):
        """認証（ログイン）処理の非同期実装"""
        await self.initialize_browser()
        try:
            authenticated = await self.authenticate(username, password)
            self.authenticated = authenticated
            return authenticated
        except Exception as e:
            logger.error(f"認証中にエラーが発生しました: {e}")
            return False
        finally:
            await self.close_browser()
    
    async def _search_products(self, keyword, max_items=10):
        """商品検索の非同期実装"""
        if not await self.initialize_browser():
            return []
        try:
            return await self.search_products(keyword, max_items)
        except Exception as e:
            logger.error(f"商品検索中にエラーが発生しました: {e}")
            return []
        finally:
            await self.close_browser()
    
    async def _get_product_details(self, product_id):
        """商品詳細取得の非同期実装"""
        if not await self.initialize_browser():
            return None
        try:
            return await self.get_product_details(product_id)
        except Exception as e:
            logger.error(f"商品詳細取得中にエラーが発生しました: {e}")
            return None
        finally:
            await self.close_browser()
    
    async def _get_purchase_history(self, start_date=None, end_date=None, max_pages=1):
        """購入履歴取得の非同期実装"""
        if not await self.initialize_browser():
            return []
        try:
            return await self.get_purchase_history(start_date, end_date, max_pages)
        except Exception as e:
            logger.error(f"購入履歴取得中にエラーが発生しました: {e}")
            return []
        finally:
            await self.close_browser()