from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app import db
from app.models.product import Product
from app.models.purchase import Purchase
from app.models.watchlist import WatchlistItem

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
    if sort_by == 'price_asc':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'date_desc':
        query = query.order_by(Product.release_date.desc())
    else:  # デフォルトはタイトル順
        query = query.order_by(Product.title)
    
    # ページネーション
    page = request.args.get('page', 1, type=int)
    per_page = 20  # 1ページあたりの表示件数
    products = query.paginate(page=page, per_page=per_page)
    
    return render_template('products.html', 
                          products=products,
                          platform=platform,
                          search_query=search_query,
                          sort_by=sort_by)

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
    
    return render_template('product_detail.html', 
                          product=product,
                          purchase=purchase,
                          related_products=related_products)

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
                
            return redirect(url_for('main.product_detail', id=new_product.id))
        
        except Exception as e:
            db.session.rollback()
            return render_template('add_product.html', error=str(e))
    
    return render_template('add_product.html')

@main_bp.route('/purchases')
def purchase_list():
    """購入履歴一覧を表示"""
    # クエリパラメータからフィルタ条件を取得
    platform = request.args.get('platform', '')
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'date_desc')
    
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
    if sort_by == 'date_asc':
        query = query.order_by(Purchase.purchased_date.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Purchase.purchased_price.desc())
    elif sort_by == 'price_asc':
        query = query.order_by(Purchase.purchased_price.asc())
    else:  # デフォルトは購入日の降順
        query = query.order_by(Purchase.purchased_date.desc())
    
    # ページネーション
    page = request.args.get('page', 1, type=int)
    per_page = 20  # 1ページあたりの表示件数
    purchases = query.paginate(page=page, per_page=per_page)
    
    return render_template('purchases.html', 
                          purchases=purchases,
                          platform=platform,
                          search_query=search_query,
                          sort_by=sort_by)

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
            return redirect(url_for('main.purchase_list'))
        except Exception as e:
            db.session.rollback()
            return render_template('add_purchase.html', 
                                 products=Product.query.all(),
                                 error=str(e))
    
    # 商品リストを取得してフォームを表示
    products = Product.query.order_by(Product.title).all()
    return render_template('add_purchase.html', products=products)

@main_bp.route('/duplicates')
def check_duplicates():
    """重複している可能性のある商品を検索して表示"""
    # 実装はフェーズ2で詳細化
    # 現在はダミーデータを返す
    return render_template('duplicates.html', duplicates=[])

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