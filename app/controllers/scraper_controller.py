#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app import db
from app.models.product import Product
from app.models.purchase import Purchase
from app.utils.dmm_scraper import DmmScraper
from app.utils.dlsite_scraper import DlsiteScraper

# ロガーの設定
logger = logging.getLogger(__name__)

# Blueprintの作成
scraper_bp = Blueprint('scraper', __name__, url_prefix='/scraper')

# スクレイパーのインスタンスを作成
dmm_scraper = DmmScraper()
dlsite_scraper = DlsiteScraper()

@scraper_bp.route('/search', methods=['GET', 'POST'])
def search():
    """
    商品検索ページ
    検索キーワードを受け取り、DMMまたはDLsiteで検索を実行する
    """
    results = []
    platform = 'dmm'
    keyword = ''
    
    if request.method == 'POST':
        keyword = request.form.get('keyword', '')
        platform = request.form.get('platform', 'dmm')
        max_results = int(request.form.get('max_results', 20))
        
        if keyword:
            try:
                if platform == 'dmm':
                    results = dmm_scraper.search_products(keyword, max_items=max_results)
                elif platform == 'dlsite':
                    results = dlsite_scraper.search_products(keyword, max_items=max_results)
                else:
                    flash('不明なプラットフォームです', 'danger')
                    
                # 検索結果の商品が既にDBにあるかどうかをチェック
                for product in results:
                    platform_id = product['platform_id']
                    existing_product = Product.query.filter_by(
                        platform=platform, platform_id=platform_id
                    ).first()
                    product['exists_in_db'] = existing_product is not None
                    
            except Exception as e:
                logger.error(f"商品検索中にエラーが発生しました: {str(e)}")
                flash(f'検索中にエラーが発生しました: {str(e)}', 'danger')
    
    return render_template('scraper/search.html', 
                         results=results, 
                         platform=platform, 
                         keyword=keyword)

@scraper_bp.route('/product_details/<platform>/<product_id>')
def product_details(platform, product_id):
    """
    商品詳細情報の取得と表示
    """
    details = {}
    exists_in_db = False
    purchase_info = None
    error = None
    
    try:
        # データベースで既存の商品を確認
        existing_product = Product.query.filter_by(
            platform=platform, platform_id=product_id
        ).first()
        
        exists_in_db = existing_product is not None
        
        # 商品が存在する場合、購入情報も取得
        if exists_in_db:
            purchase_info = Purchase.query.filter_by(product_id=existing_product.id).first()
        
        # プラットフォームに応じたスクレイパーを使用
        if platform == 'dmm':
            details = dmm_scraper.get_product_details(product_id)
        elif platform == 'dlsite':
            details = dlsite_scraper.get_product_details(product_id)
        else:
            error = '不明なプラットフォームです'
            
    except Exception as e:
        logger.error(f"商品詳細の取得中にエラーが発生しました: {str(e)}")
        error = f'商品詳細の取得中にエラーが発生しました: {str(e)}'
    
    return render_template('scraper/product_details.html', 
                         details=details, 
                         exists_in_db=exists_in_db,
                         purchase_info=purchase_info,
                         error=error)

@scraper_bp.route('/import_product', methods=['POST'])
def import_product():
    """
    スクレイピングした商品情報をDBにインポートする
    """
    platform = request.form.get('platform')
    product_id = request.form.get('product_id')
    add_purchase = request.form.get('add_purchase') == 'on'
    
    try:
        # 既存の商品をチェック
        existing_product = Product.query.filter_by(
            platform=platform, platform_id=product_id
        ).first()
        
        if existing_product:
            flash('この商品は既にデータベースに存在します', 'warning')
            return redirect(url_for('main.product_detail', id=existing_product.id))
        
        # 商品詳細を取得
        details = None
        if platform == 'dmm':
            details = dmm_scraper.get_product_details(product_id)
        elif platform == 'dlsite':
            details = dlsite_scraper.get_product_details(product_id)
        else:
            flash('不明なプラットフォームです', 'danger')
            return redirect(url_for('scraper.search'))
        
        if not details:
            flash('商品詳細を取得できませんでした', 'danger')
            return redirect(url_for('scraper.search'))
        
        # 商品情報を登録
        release_date = None
        if 'release_date' in details and details['release_date']:
            release_date = datetime.fromisoformat(details['release_date']).date()
            
        new_product = Product(
            title=details.get('title', '不明なタイトル'),
            platform=platform,
            platform_id=product_id,
            url=details.get('url', ''),
            price=details.get('price', 0),
            discount_price=details.get('discount_price'),
            maker=details.get('maker', ''),
            release_date=release_date,
            thumbnail_url=details.get('thumbnail_url', ''),
            category=details.get('category', ''),
            last_updated=datetime.now()
        )
        
        db.session.add(new_product)
        db.session.commit()
        
        # 購入情報も同時に登録
        if add_purchase:
            new_purchase = Purchase(
                product_id=new_product.id,
                purchased_date=datetime.now().date(),
                purchased_price=details.get('price', 0),
                purchase_type='通常'
            )
            db.session.add(new_purchase)
            db.session.commit()
            flash('商品と購入情報をインポートしました', 'success')
        else:
            flash('商品をインポートしました', 'success')
            
        return redirect(url_for('main.product_detail', id=new_product.id))
        
    except Exception as e:
        logger.error(f"商品のインポート中にエラーが発生しました: {str(e)}")
        flash(f'商品のインポート中にエラーが発生しました: {str(e)}', 'danger')
        return redirect(url_for('scraper.search'))

@scraper_bp.route('/bulk_search', methods=['GET', 'POST'])
def bulk_search():
    """
    複数のキーワードを一括検索する
    """
    if request.method == 'POST':
        keywords = request.form.get('keywords', '').strip().split('\n')
        platform = request.form.get('platform', 'dmm')
        max_results_per_keyword = int(request.form.get('max_results', 5))
        
        # 空白行を削除
        keywords = [k.strip() for k in keywords if k.strip()]
        
        if not keywords:
            flash('検索キーワードを入力してください', 'warning')
            return render_template('scraper/bulk_search.html')
        
        # 結果を格納するリスト
        all_results = []
        
        try:
            for keyword in keywords:
                if platform == 'dmm':
                    results = dmm_scraper.search_products(keyword, max_items=max_results_per_keyword)
                elif platform == 'dlsite':
                    results = dlsite_scraper.search_products(keyword, max_items=max_results_per_keyword)
                else:
                    continue
                    
                # 検索結果の商品が既にDBにあるかどうかをチェック
                for product in results:
                    platform_id = product['platform_id']
                    existing_product = Product.query.filter_by(
                        platform=platform, platform_id=platform_id
                    ).first()
                    product['exists_in_db'] = existing_product is not None
                    product['search_keyword'] = keyword  # 検索キーワードを追加
                
                all_results.extend(results)
                
            return render_template('scraper/bulk_search.html', 
                                 all_results=all_results, 
                                 platform=platform,
                                 keywords='\n'.join(keywords))
        
        except Exception as e:
            logger.error(f"一括検索中にエラーが発生しました: {str(e)}")
            flash(f'一括検索中にエラーが発生しました: {str(e)}', 'danger')
    
    return render_template('scraper/bulk_search.html')

@scraper_bp.route('/api/search', methods=['GET'])
def api_search():
    """
    商品検索APIエンドポイント
    """
    keyword = request.args.get('keyword', '')
    platform = request.args.get('platform', 'dmm')
    max_results = int(request.args.get('max_results', 10))
    
    if not keyword:
        return jsonify({'error': 'キーワードが指定されていません'}), 400
    
    try:
        if platform == 'dmm':
            results = dmm_scraper.search_products(keyword, max_items=max_results)
        elif platform == 'dlsite':
            results = dlsite_scraper.search_products(keyword, max_items=max_results)
        else:
            return jsonify({'error': '不明なプラットフォーム'}), 400
            
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"API検索中にエラーが発生しました: {str(e)}")
        return jsonify({'error': str(e)}), 500