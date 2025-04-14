from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app import db
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.watchlist import WatchlistItem
from sqlalchemy import func, or_, and_, desc
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

@main_bp.route('/products')
def product_list():
    """商品リストを表示"""
    # クエリパラメータからフィルタ条件を取得
    platform = request.args.get('platform', '')
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'title')
    sort_dir = request.args.get('dir', 'asc')
    
    # 商品の検索クエリを構築
    query = Product.query
    
    # プラットフォームでフィルタ
    if platform:
        query = query.filter(Product.platform == platform)
    
    # 検索クエリでフィルタ
    if search_query:
        query = query.filter(
            (Product.title.ilike(f'%{search_query}%')) | 
            (Product.maker.ilike(f'%{search_query}%'))
        )
    
    # ソート条件の適用
    if sort_by == 'price':
        order_col = Product.price
    elif sort_by == 'date':
        order_col = Product.release_date
    else:  # デフォルトはタイトル順
        order_col = Product.title
    
    if sort_dir == 'desc':
        order_col = order_col.desc()
    
    query = query.order_by(order_col)
    
    # ページネーション
    page = request.args.get('page', 1, type=int)
    per_page = 20  # 1ページあたりの表示件数
    products = query.paginate(page=page, per_page=per_page)
    
    # 購入済み商品のIDを取得
    purchased_ids = db.session.query(Purchase.product_id).distinct().all()
    purchased_ids = [id[0] for id in purchased_ids]
    
    return render_template('products.html', 
                          products=products,
                          platform=platform,
                          search_query=search_query,
                          sort_by=sort_by,
                          sort_dir=sort_dir,
                          purchased_ids=purchased_ids)

@main_bp.route('/product/<int:id>')
def product_detail(id):
    """商品の詳細ページを表示"""
    product = Product.query.get_or_404(id)
    purchase = Purchase.query.filter_by(product_id=id).first()
    
    # 同じ作者/サークルの他の商品を取得
    related_products = []
    if product.maker:
        related_products = Product.query\
            .filter(Product.maker == product.maker, Product.id != id)\
            .limit(5).all()
    
    purchases = Purchase.query.filter_by(product_id=id).all()
    
    return render_template('product_detail.html', 
                          product=product,
                          purchase=purchase,
                          related_products=related_products,
                          purchases=purchases)

@main_bp.route('/add_product', methods=['GET', 'POST'])
def add_product():
    """商品の手動追加ページ"""
    if request.method == 'POST':
        # フォームからデータを取得
        title = request.form.get('title')
        platform = request.form.get('platform')
        platform_id = request.form.get('platform_id')
        url = request.form.get('url')
        price = request.form.get('price')
        maker = request.form.get('maker')
        release_date_str = request.form.get('release_date')
        
        # 日付の変換
        release_date = None
        if release_date_str:
            try:
                release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
            except ValueError:
                # 日付形式が無効な場合は何もしない
                pass
        
        # 新しい商品を作成
        new_product = Product(
            title=title,
            platform=platform,
            platform_id=platform_id,
            url=url,
            price=price,
            maker=maker,
            release_date=release_date
        )
        
        db.session.add(new_product)
        
        try:
            db.session.commit()
            flash(f'商品「{title}」を追加しました', 'success')
            # 購入情報も同時に登録する場合
            if 'add_purchase' in request.form:
                purchase_date_str = request.form.get('purchase_date')
                purchase_price = request.form.get('purchase_price')
                
                purchase_date = None
                if purchase_date_str:
                    try:
                        purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        purchase_date = datetime.now().date()
                else:
                    purchase_date = datetime.now().date()
                
                new_purchase = Purchase(
                    product_id=new_product.id,
                    purchased_date=purchase_date,
                    purchased_price=purchase_price or price,
                    purchase_type=request.form.get('purchase_type', '通常')
                )
                
                db.session.add(new_purchase)
                db.session.commit()
                flash('購入情報も記録しました', 'success')
                
            return redirect(url_for('main.product_detail', id=new_product.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'エラーが発生しました: {str(e)}', 'danger')
            return render_template('add_product.html', error=str(e))
    
    return render_template('add_product.html')

@main_bp.route('/purchases')
def purchase_list():
    """購入履歴一覧を表示"""
    # クエリパラメータからフィルタ条件を取得
    platform = request.args.get('platform', '')
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'date_desc')
    sort_dir = request.args.get('dir', 'desc')
    
    # 購入履歴の検索クエリを構築
    query = db.session.query(Purchase, Product).join(Product)
    
    # プラットフォームでフィルタ
    if platform:
        query = query.filter(Product.platform == platform)
    
    # 検索クエリでフィルタ
    if search_query:
        query = query.filter(
            (Product.title.ilike(f'%{search_query}%')) | 
            (Product.maker.ilike(f'%{search_query}%'))
        )
    
    # ソート条件の適用
    if sort_by == 'date':
        order_col = Purchase.purchased_date
    elif sort_by == 'price':
        order_col = Purchase.purchased_price
    elif sort_by == 'title':
        order_col = Product.title
    else:  # デフォルトは購入日の降順
        order_col = Purchase.purchased_date
    
    if sort_dir == 'desc':
        order_col = order_col.desc()
    
    query = query.order_by(order_col)
    
    # ページネーション
    page = request.args.get('page', 1, type=int)
    per_page = 20  # 1ページあたりの表示件数
    purchases = query.paginate(page=page, per_page=per_page)
    
    # 合計購入金額
    total_spent = sum(p[0].purchased_price for p in purchases.items if p[0].purchased_price)
    
    return render_template('purchases.html', 
                          purchases=purchases,
                          platform=platform,
                          search_query=search_query,
                          sort_by=sort_by,
                          sort_dir=sort_dir,
                          total_spent=total_spent)

@main_bp.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():
    """購入履歴の追加"""
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        purchase_date_str = request.form.get('purchase_date')
        purchased_price = request.form.get('purchased_price')
        purchase_type = request.form.get('purchase_type', '通常')
        note = request.form.get('note', '')
        
        # 商品の存在確認
        product = Product.query.get_or_404(product_id)
        
        # 日付の変換
        purchase_date = None
        if purchase_date_str:
            try:
                purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
            except ValueError:
                purchase_date = datetime.now().date()
        else:
            purchase_date = datetime.now().date()
        
        # 新しい購入履歴を作成
        new_purchase = Purchase(
            product_id=product_id,
            purchased_date=purchase_date,
            purchased_price=purchased_price or product.price,
            purchase_type=purchase_type,
            note=note
        )
        
        db.session.add(new_purchase)
        
        try:
            db.session.commit()
            flash(f'「{product.title}」の購入情報を追加しました', 'success')
            return redirect(url_for('main.purchase_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'エラーが発生しました: {str(e)}', 'danger')
            return render_template('add_purchase.html', 
                                 products=Product.query.all(),
                                 error=str(e))
    
    # 商品リストを取得してフォームを表示
    products = Product.query.order_by(Product.title).all()
    return render_template('add_purchase.html', products=products)

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
    
    # 既存のシンプルな重複検出方法を使うかどうか
    use_legacy = request.args.get('legacy', 'false') == 'true'
    
    duplicates = []
    
    if use_legacy:
        # 旧来の単純な重複チェック（修正なし）
        all_products = Product.query.all()
        duplicate_groups = []
        processed = set()
        TITLE_SIMILARITY_THRESHOLD = 0.8
        
        # 重複チェックロジック（既存コードを維持）
        for i, product1 in enumerate(all_products):
            # 既に処理済みならスキップ
            if product1.id in processed:
                continue
            
            # 新しい重複グループ
            current_group = [product1]
            processed.add(product1.id)
            
            # 正規化されたタイトル
            normalized_title1 = _normalize_title(product1.title)
            
            for j in range(i + 1, len(all_products)):
                product2 = all_products[j]
                
                # 既に処理済みならスキップ
                if product2.id in processed:
                    continue
                
                # タイトル類似度チェック
                normalized_title2 = _normalize_title(product2.title)
                title_similarity = difflib.SequenceMatcher(None, normalized_title1, normalized_title2).ratio()
                
                # メーカー/サークル一致チェック
                maker_match = (product1.maker and product2.maker and 
                              product1.maker.lower() == product2.maker.lower())
                
                # カテゴリ一致チェック
                category_match = (product1.category and product2.category and 
                                 product1.category.lower() == product2.category.lower())
                
                # 最終的な判定
                is_duplicate = False
                
                # タイトルが非常に似ている場合
                if title_similarity > TITLE_SIMILARITY_THRESHOLD:
                    # メーカーまたはカテゴリも一致する場合、確実に重複
                    if maker_match or category_match:
                        is_duplicate = True
                    # それ以外でも、タイトルの類似度がかなり高い場合は重複候補
                    elif title_similarity > 0.9:
                        is_duplicate = True
                
                # メーカーが一致し、タイトルもある程度似ている場合も重複候補
                elif maker_match and title_similarity > 0.6:
                    is_duplicate = True
                
                if is_duplicate:
                    current_group.append(product2)
                    processed.add(product2.id)
            
            # グループに複数のアイテムがある場合のみ追加
            if len(current_group) > 1:
                duplicate_groups.append(current_group)
        
        # テンプレート用にデータを変換
        for group in duplicate_groups:
            for i in range(len(group) - 1):
                for j in range(i+1, len(group)):
                    # 2製品間の価格差を計算
                    price_diff = group[i].price - group[j].price if group[i].price and group[j].price else 0
                    # タイトル類似度を計算
                    title_similarity = difflib.SequenceMatcher(
                        None, 
                        _normalize_title(group[i].title),
                        _normalize_title(group[j].title)
                    ).ratio()
                    
                    duplicates.append({
                        'product1': group[i],
                        'product2': group[j],
                        'similarity': title_similarity,
                        'price_diff': price_diff,
                        'is_same_platform': group[i].platform == group[j].platform
                    })
    else:
        # 新しい高度な重複検出アルゴリズムを使用
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
                          use_circle=use_circle,
                          use_legacy=use_legacy)

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