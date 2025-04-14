#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import logging
import time
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, List, Optional, Any, Union

# ロガーの設定
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ScraperBase(abc.ABC):
    """
    スクレイパーの基底クラス。
    DMMとDLsiteのスクレイパーに共通する機能を提供する。
    """
    
    def __init__(self, delay: float = 1.0, timeout: int = 10, max_retries: int = 3):
        """
        Parameters
        ----------
        delay: float
            リクエスト間の遅延（秒）。サイトに負荷をかけすぎないため。
        timeout: int
            リクエストのタイムアウト（秒）
        max_retries: int
            リクエストの最大リトライ回数
        """
        self.delay = delay
        self.timeout = timeout
        self.max_retries = max_retries
        self.last_request_time = 0
        
        # セッション設定
        self.session = requests.Session()
        retries = Retry(
            total=max_retries,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))
        
        # ユーザーエージェントの設定
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7',
        }

    def _get_page(self, url: str) -> BeautifulSoup:
        """
        指定されたURLからHTMLを取得し、BeautifulSoupオブジェクトを返す
        
        Parameters
        ----------
        url: str
            取得するURL
            
        Returns
        -------
        BeautifulSoup
            解析されたHTMLコンテンツ
        """
        # レート制限を守るための遅延
        current_time = time.time()
        if current_time - self.last_request_time < self.delay:
            time.sleep(self.delay - (current_time - self.last_request_time))
        
        try:
            logger.info(f"GETリクエスト送信: {url}")
            response = self.session.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout
            )
            self.last_request_time = time.time()
            
            response.raise_for_status()  # 200 OK以外のステータスコードでエラーを発生させる
            logger.info(f"リクエスト成功: {url}, ステータスコード: {response.status_code}")
            
            # HTMLの解析
            return BeautifulSoup(response.content, 'html.parser')
            
        except requests.exceptions.RequestException as e:
            logger.error(f"リクエスト中にエラーが発生しました: {url}, エラー: {str(e)}")
            raise
    
    @abc.abstractmethod
    def search_products(self, keyword: str, max_items: int = 20) -> List[Dict[str, Any]]:
        """
        キーワードで商品を検索する
        
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
        pass
    
    @abc.abstractmethod
    def get_product_details(self, product_id: str) -> Dict[str, Any]:
        """
        商品の詳細情報を取得する
        
        Parameters
        ----------
        product_id: str
            商品ID
            
        Returns
        -------
        Dict[str, Any]
            商品の詳細情報
        """
        pass
    
    def normalize_price(self, price_text: str) -> Optional[int]:
        """
        価格テキストを正規化して整数値に変換する
        
        Parameters
        ----------
        price_text: str
            価格テキスト（例: "¥1,200" や "1,200円"）
            
        Returns
        -------
        Optional[int]
            正規化された価格（整数）、変換できない場合はNone
        """
        if not price_text:
            return None
            
        # 不要な文字を削除
        cleaned = price_text.replace('¥', '').replace('￥', '').replace(',', '').replace('円', '').strip()
        
        try:
            return int(cleaned)
        except ValueError:
            logger.warning(f"価格の変換に失敗しました: {price_text}")
            return None