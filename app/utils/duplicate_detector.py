#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import logging
from typing import List, Dict, Tuple, Any, Optional
import numpy as np
from Levenshtein import ratio as levenshtein_ratio
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.models.product import Product

# ロガーの設定
logger = logging.getLogger(__name__)

class DuplicateDetector:
    """
    DMMとDLsite間の重複商品を検出するためのクラス
    タイトル類似性、サークル名一致などの複数の手法を組み合わせて重複検出を行う
    """
    
    def __init__(self, title_similarity_threshold: float = 0.75, 
                 use_circle_name: bool = True,
                 use_tf_idf: bool = True):
        """
        Parameters
        ----------
        title_similarity_threshold: float
            タイトル類似度の閾値（この値以上なら類似と判定）
        use_circle_name: bool
            サークル名も比較に利用するかどうか
        use_tf_idf: bool
            TF-IDF + コサイン類似度を使用するかどうか（Falseの場合はレーベンシュタイン距離のみ）
        """
        self.title_threshold = title_similarity_threshold
        self.use_circle_name = use_circle_name
        self.use_tf_idf = use_tf_idf
        
        # TF-IDFベクトライザの初期化
        self.vectorizer = TfidfVectorizer(
            analyzer='char_wb',  # 文字ベースの分析（日本語に適している）
            ngram_range=(2, 3),  # 2~3文字のn-gramを使用
            min_df=1,
            max_df=0.9
        )
        
    def find_duplicates(self, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        DMM商品とDLsite商品間の潜在的な重複を検出する
        
        Parameters
        ----------
        max_results: int
            返す最大結果数
            
        Returns
        -------
        List[Dict[str, Any]]
            検出された重複候補のリスト
        """
        # DMMとDLsiteの商品を取得
        dmm_products = Product.query.filter_by(platform='dmm').all()
        dlsite_products = Product.query.filter_by(platform='dlsite').all()
        
        logger.info(f"重複検出を開始: DMM商品 {len(dmm_products)}件, DLsite商品 {len(dlsite_products)}件")
        
        # 比較結果を格納するリスト
        similarities = []
        
        # タイトルの前処理を一括で行う（速度向上のため）
        dmm_titles = [self._preprocess_title(product.title) for product in dmm_products]
        dlsite_titles = [self._preprocess_title(product.title) for product in dlsite_products]
        
        # TF-IDFを使用する場合は先に計算しておく
        if self.use_tf_idf:
            # すべてのタイトルでベクトライザをフィット
            all_titles = dmm_titles + dlsite_titles
            try:
                # TF-IDFベクトルを計算
                tfidf_matrix = self.vectorizer.fit_transform(all_titles)
                dmm_tfidf = tfidf_matrix[:len(dmm_titles)]
                dlsite_tfidf = tfidf_matrix[len(dmm_titles):]
            except Exception as e:
                logger.error(f"TF-IDF計算中にエラーが発生: {e}")
                self.use_tf_idf = False  # エラーが発生したらTF-IDFを使用しない
        
        # 各組み合わせで類似度を計算
        for i, dmm_product in enumerate(dmm_products):
            for j, dlsite_product in enumerate(dlsite_products):
                try:
                    # 類似度計算
                    similarity_score = 0
                    
                    # TF-IDFとコサイン類似度を使用
                    if self.use_tf_idf:
                        # コサイン類似度を計算（0-1の範囲）
                        cos_sim = cosine_similarity(
                            dmm_tfidf[i:i+1], dlsite_tfidf[j:j+1]
                        )[0][0]
                        similarity_score = cos_sim
                    else:
                        # レーベンシュタイン距離を計算（0-1の範囲）
                        lev_similarity = levenshtein_ratio(dmm_titles[i], dlsite_titles[j])
                        similarity_score = lev_similarity
                    
                    # サークル名が一致した場合にスコアを上げる
                    maker_bonus = 0
                    if self.use_circle_name and dmm_product.maker and dlsite_product.maker:
                        dmm_maker = self._normalize_maker_name(dmm_product.maker)
                        dlsite_maker = self._normalize_maker_name(dlsite_product.maker)
                        
                        # サークル名の類似度も計算
                        maker_similarity = levenshtein_ratio(dmm_maker, dlsite_maker)
                        
                        if maker_similarity > 0.9:  # 90%以上一致ならほぼ同じと見なす
                            maker_bonus = 0.2  # サークル名が一致した場合のボーナス
                    
                    # 最終的な類似度スコア（サークル一致ボーナスを考慮）
                    final_score = min(similarity_score + maker_bonus, 1.0)
                    
                    # 閾値を超えたら結果に追加
                    if final_score >= self.title_threshold:
                        similarities.append({
                            'dmm_product': dmm_product,
                            'dlsite_product': dlsite_product,
                            'similarity': final_score,
                            'maker_match': maker_bonus > 0
                        })
                        
                except Exception as e:
                    logger.error(f"類似度計算中にエラー: {e}")
                    continue
        
        # 類似度の高い順にソート
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        logger.info(f"重複検出完了: {len(similarities)}件の候補が見つかりました")
        
        # 結果を制限
        return similarities[:max_results]
    
    def _preprocess_title(self, title: str) -> str:
        """
        タイトルの前処理を行う
        
        Parameters
        ----------
        title: str
            前処理するタイトル文字列
            
        Returns
        -------
        str
            前処理されたタイトル文字列
        """
        if not title:
            return ""
            
        # 小文字化
        text = title.lower()
        
        # 特殊記号を削除
        text = re.sub(r'[【】「」『』（）\[\]\(\)\{\}]', ' ', text)
        
        # 連続する空白を1つにまとめる
        text = re.sub(r'\s+', ' ', text)
        
        # 前後の空白を削除
        return text.strip()
    
    def _normalize_maker_name(self, maker: str) -> str:
        """
        メーカー/サークル名を正規化する
        
        Parameters
        ----------
        maker: str
            正規化するメーカー/サークル名
            
        Returns
        -------
        str
            正規化されたメーカー/サークル名
        """
        if not maker:
            return ""
            
        # 小文字化
        text = maker.lower()
        
        # 特殊記号を削除
        text = re.sub(r'[【】「」『』（）\[\]\(\)\{\}]', '', text)
        
        # 連続する空白を1つにまとめる
        text = re.sub(r'\s+', ' ', text)
        
        # 前後の空白を削除
        return text.strip()
    
    @staticmethod
    def check_known_duplicates() -> List[Dict[str, Any]]:
        """
        既知の重複パターンを検索する
        特定のサークルや命名規則でDMMとDLsiteで同じ商品を検出

        Returns
        -------
        List[Dict[str, Any]]
            検出された既知の重複のリスト
        """
        # このメソッドは特定のサークルやパターンに基づく既知の重複を検出する
        # 例: サークルAはDMMでの商品IDがXXXXXで、DLsiteではRJXXXXXの形式を使用している場合など
        
        # 実装部分は省略（必要に応じて追加）
        return []