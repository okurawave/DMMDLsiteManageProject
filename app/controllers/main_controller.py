from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, flash
from app import db
from app.models.product import Product
from app.models.purchase import Purchase
from sqlalchemy import func, desc
import re
import difflib
import logging
from app.utils.duplicate_detector import DuplicateDetector

# ロガーの設定
logger = logging.getLogger(__name__)

# Blueprintの作成
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """メインページを表示"""
    # 最新の購入履歴を取得
    recent_purchases = db.session.query(Purchase, Product)\
        .join(Product)\
        .order_by(Purchase.purchased_date.desc())\
        .limit(10).all()
    
    # 購入履歴の総数を取得
    purchase_count = Purchase.query.count()
    
    # DMMとDLsiteでの購入数を取得
    dmm_count = db.session.query(Purchase).join(Product)\
        .filter(Product.platform == 'dmm').count()
    dlsite_count = db.session.query(Purchase).join(Product)\
        .filter(Product.platform == 'dlsite').count()
    
    # 統計情報
    stats = {
        'total_purchases': purchase_count,
        'dmm_count': dmm_count,
        'dlsite_count': dlsite_count
    }
    
    # 基本統計情報の取得
    stats['total_products'] = Product.query.count()
    stats['purchased_products'] = db.session.query(Purchase).distinct(Purchase.product_id).count()
    total_spent = db.session.query(func.sum(Purchase.purchased_price)).scalar()
    stats['total_spent'] = total_spent or 0
    platform_counts = db.session.query(
        Product.platform, func.count(Product.id)
    ).group_by(Product.platform).all()
    stats['platform_counts'] = dict(platform_counts)
    
    return render_template('index.html', 
                          recent_purchases=recent_purchases, 
                          stats=stats)

@main_bp.route('/duplicates')
def check_duplicates():
    """
    高度な重複チェックを実行
    タイトル、メーカー、カテゴリ、価格などを考慮した重複検出
    """
    # リクエストからパラメータを取得
    threshold = float(request.args.get('threshold', 0.75))
    max_results = int(request.args.get('max_results', 50))
    use_tfidf = request.args.get('algo', 'tfidf') == 'tfidf'
    use_circle = request.args.get('use_circle', 'true') == 'true'
    
    duplicates = []
    
    # 高度な重複検出アルゴリズムを使用
    try:
        detector = DuplicateDetector(
            title_similarity_threshold=threshold, 
            use_circle_name=use_circle,
            use_tf_idf=use_tfidf
        )
        duplicate_results = detector.find_duplicates(max_results=max_results)
        
        # テンプレート用にデータを整形
        for result in duplicate_results:
            dmm_product = result['dmm_product']
            dlsite_product = result['dlsite_product']
            similarity = result['similarity']
            
            # 価格差を計算
            price_diff = 0
            if dmm_product.price and dlsite_product.price:
                price_diff = dmm_product.price - dlsite_product.price
            
            duplicates.append({
                'dmm_product': dmm_product,
                'dlsite_product': dlsite_product,
                'similarity': similarity,
                'price_diff': price_diff,
                'maker_match': result.get('maker_match', False)
            })
            
        logger.info(f"重複検出完了: {len(duplicates)}件の重複候補が見つかりました")
        
    except Exception as e:
        logger.error(f"重複検出中にエラーが発生しました: {str(e)}")
        flash(f'重複検出中にエラーが発生しました: {str(e)}', 'danger')
    
    return render_template('duplicates.html', 
                          duplicates=duplicates,
                          threshold=threshold,
                          max_results=max_results,
                          use_tfidf=use_tfidf,
                          use_circle=use_circle)

def _normalize_title(title):
    """タイトルの正規化"""
    if not title:
        return ""
    # カッコ内のテキストを削除
    title = re.sub(r'【[^】]*】|\[[^\]]*\]|\([^\)]*\)', '', title)
    # 特殊文字と数字を削除
    title = re.sub(r'[^\w\s]|[0-9]', '', title)
    # 空白を正規化
    title = re.sub(r'\s+', ' ', title).strip().lower()
    return title

# APIエンドポイント（Ajax用）
@main_bp.route('/api/search_products')
def api_search_products():
    """商品を検索するAPIエンドポイント"""
    search_query = request.args.get('q', '')
    platform = request.args.get('platform', '')
    
    query = Product.query
    
    if platform:
        query = query.filter(Product.platform == platform)
    
    if search_query:
        query = query.filter(
            (Product.title.ilike(f'%{search_query}%')) | 
            (Product.maker.ilike(f'%{search_query}%'))
        )
    
    products = query.order_by(Product.title).limit(10).all()
    return jsonify([p.to_dict() for p in products])

@main_bp.route('/api/product_details/<int:product_id>')
def api_product_details(product_id):
    """商品の詳細情報を返すAPIエンドポイント"""
    product = Product.query.get_or_404(product_id)
    purchase = Purchase.query.filter_by(product_id=product_id).first()
    
    result = product.to_dict()
    if purchase:
        result['purchase'] = {
            'purchased_date': purchase.purchased_date.isoformat() if purchase.purchased_date else None,
            'purchased_price': purchase.purchased_price,
            'purchase_type': purchase.purchase_type,
            'note': purchase.note
        }
    
    return jsonify(result)

@main_bp.route('/api/compare_products')
def api_compare_products():
    """2つの商品を比較するAPIエンドポイント"""
    product1_id = request.args.get('product1_id', type=int)
    product2_id = request.args.get('product2_id', type=int)
    
    if not product1_id or not product2_id:
        return jsonify({'error': '商品IDが不正です'}), 400
    
    product1 = Product.query.get_or_404(product1_id)
    product2 = Product.query.get_or_404(product2_id)
    
    # 同じ商品かどうかの確認
    is_same_product = False
    
    # タイトル類似度
    title_similarity = 0
    normalized_title1 = _normalize_title(product1.title)
    normalized_title2 = _normalize_title(product2.title)
    if normalized_title1 and normalized_title2:
        title_similarity = difflib.SequenceMatcher(
            None, normalized_title1, normalized_title2
        ).ratio()
    
    # メーカー/サークル名一致
    maker_match = False
    if product1.maker and product2.maker:
        maker_match = product1.maker.lower() == product2.maker.lower()
    
    # 価格比較
    price_difference = None
    price_diff_percentage = None
    if product1.price and product2.price and product1.price > 0 and product2.price > 0:
        price_difference = product1.price - product2.price
        price_diff_percentage = (abs(price_difference) / max(product1.price, product2.price)) * 100
    
    # 高度な類似度計算
    advanced_similarity = None
    try:
        if product1.platform != product2.platform:
            # DMMとDLsiteの間でのみ高度な類似度計算を行う
            dmm_product = product1 if product1.platform == 'dmm' else product2
            dlsite_product = product1 if product1.platform == 'dlsite' else product2
            
            detector = DuplicateDetector(use_tf_idf=True)
            # 前処理したタイトルでTF-IDFコサイン類似度を計算
            similarity = detector._calculate_similarity(
                detector._preprocess_title(dmm_product.title),
                detector._preprocess_title(dlsite_product.title)
            )
            advanced_similarity = similarity
    except Exception as e:
        logger.error(f"高度な類似度計算中にエラーが発生: {e}")
    
    # 判定結果
    if title_similarity > 0.9 or (title_similarity > 0.7 and maker_match):
        is_same_product = True
    
    comparison = {
        'product1': product1.to_dict(),
        'product2': product2.to_dict(),
        'comparison': {
            'title_similarity': title_similarity,
            'maker_match': maker_match,
            'price_difference': price_difference,
            'price_diff_percentage': price_diff_percentage,
            'advanced_similarity': advanced_similarity,
            'is_same_product': is_same_product
        }
    }
    
    return jsonify(comparison)

@main_bp.route('/api/price_history/<int:product_id>')
def api_price_history(product_id):
    """商品の価格履歴を取得するAPIエンドポイント（将来的に実装）"""
    product = Product.query.get_or_404(product_id)
    
    # 将来的に価格履歴を保存するテーブルからデータを取得
    # 現在はダミーデータを返す
    dummy_history = []
    
    # 現在の価格をダミーデータに追加
    if product.price:
        dummy_history.append({
            'date': datetime.now().date().isoformat(),
            'price': product.price,
            'source': 'current'
        })
    
    # 購入履歴からの価格
    purchases = Purchase.query.filter_by(product_id=product_id).all()
    for p in purchases:
        if p.purchased_price:
            dummy_history.append({
                'date': p.purchased_date.isoformat() if p.purchased_date else None,
                'price': p.purchased_price,
                'source': 'purchase'
            })
    
    return jsonify({
        'product': product.to_dict(),
        'price_history': dummy_history
    })