from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.product import Product
from app.models.purchase import Purchase
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

# Blueprintの作成
product_bp = Blueprint('product', __name__, url_prefix='/product')

@product_bp.route('/')
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
                          purchased_ids=purchased_ids,
                          platform=platform,
                          search_query=search_query,
                          sort_by=sort_by,
                          sort_dir=sort_dir)

@product_bp.route('/add', methods=['GET', 'POST'])
def add_product():
    """商品の追加"""
    if request.method == 'POST':
        try:
            # フォームからデータを取得
            title = request.form.get('title')
            platform = request.form.get('platform')
            platform_id = request.form.get('platform_id')
            price = request.form.get('price')
            maker = request.form.get('maker')
            release_date_str = request.form.get('release_date')
            url = request.form.get('url')
            
            # 必須フィールドのバリデーション
            if not title:
                raise ValueError('タイトルは必須です')
            if not platform:
                raise ValueError('プラットフォームを選択してください')
            if not platform_id:
                raise ValueError('プラットフォームIDは必須です')
            if not price:
                raise ValueError('価格を入力してください')
            
            # 同じプラットフォームIDの商品がすでに存在するか確認
            existing_product = Product.query.filter_by(
                platform=platform, platform_id=platform_id
            ).first()
            if existing_product:
                raise ValueError(f'同じプラットフォームIDの商品が既に存在します (ID: {existing_product.id})')
            
            # 日付の変換
            release_date = None
            if release_date_str:
                try:
                    release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"無効な発売日フォーマット: {release_date_str}")
            
            # 新しい商品を作成
            new_product = Product(
                title=title,
                platform=platform,
                platform_id=platform_id,
                price=price,
                maker=maker,
                release_date=release_date,
                url=url
            )
            
            db.session.add(new_product)
            db.session.commit()
            
            flash(f'商品「{title}」を追加しました', 'success')
            
            # 購入履歴も同時に追加するか確認
            if 'add_purchase' in request.form:
                purchase_date_str = request.form.get('purchase_date')
                purchase_price = request.form.get('purchase_price') or price
                purchase_type = request.form.get('purchase_type', '通常')
                
                # 日付の変換
                purchase_date = None
                if purchase_date_str:
                    try:
                        purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        purchase_date = datetime.now().date()
                        logger.warning(f"無効な購入日フォーマット: {purchase_date_str}, 現在の日付を使用します")
                else:
                    purchase_date = datetime.now().date()
                
                # 新しい購入履歴を作成
                new_purchase = Purchase(
                    product_id=new_product.id,
                    purchased_date=purchase_date,
                    purchased_price=purchase_price,
                    purchase_type=purchase_type
                )
                
                db.session.add(new_purchase)
                db.session.commit()
                
                flash(f'「{title}」の購入情報も追加しました', 'success')
                return redirect(url_for('product.product_detail', id=new_product.id))
            
            return redirect(url_for('product.product_list'))
            
        except ValueError as ve:
            # バリデーションエラー
            flash(str(ve), 'danger')
            # 入力値を保持してフォームを再表示
            return render_template('add_product.html', 
                                  now=datetime.now(),
                                  form_data=request.form,
                                  error=str(ve))
            
        except Exception as e:
            # その他のエラー
            db.session.rollback()
            logger.error(f"商品追加中にエラーが発生: {str(e)}", exc_info=True)
            flash(f'エラーが発生しました: {str(e)}', 'danger')
            return render_template('add_product.html', 
                                  now=datetime.now(),
                                  form_data=request.form,
                                  error=str(e))
    
    # GETリクエスト - フォームを表示
    return render_template('add_product.html', now=datetime.now())

@product_bp.route('/<int:id>')
def product_detail(id):
    """商品詳細の表示"""
    product = Product.query.get_or_404(id)
    purchases = Purchase.query.filter_by(product_id=id).order_by(Purchase.purchased_date.desc()).all()
    return render_template('product_detail.html', product=product, purchases=purchases)

@product_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    """商品情報の編集"""
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # フォームからデータを取得して更新
            product.title = request.form.get('title')
            product.platform = request.form.get('platform')
            product.platform_id = request.form.get('platform_id')
            product.price = request.form.get('price')
            product.maker = request.form.get('maker')
            
            # 日付の変換
            release_date_str = request.form.get('release_date')
            if release_date_str:
                try:
                    product.release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"無効な発売日フォーマット: {release_date_str}, 更新しません")
            
            product.url = request.form.get('url')
            
            # 必須フィールドのバリデーション
            if not product.title:
                raise ValueError('タイトルは必須です')
            if not product.platform:
                raise ValueError('プラットフォームを選択してください')
            if not product.platform_id:
                raise ValueError('プラットフォームIDは必須です')
            if not product.price:
                raise ValueError('価格を入力してください')
            
            # プラットフォームIDの重複チェック（自分自身は除く）
            existing_product = Product.query.filter(
                Product.platform == product.platform,
                Product.platform_id == product.platform_id,
                Product.id != product.id
            ).first()
            if existing_product:
                raise ValueError(f'同じプラットフォームIDの商品が既に存在します (ID: {existing_product.id})')
            
            db.session.commit()
            
            flash(f'商品「{product.title}」の情報を更新しました', 'success')
            return redirect(url_for('product.product_detail', id=product.id))
            
        except ValueError as ve:
            # バリデーションエラー
            flash(str(ve), 'danger')
            return render_template('edit_product.html', product=product, error=str(ve))
            
        except Exception as e:
            # その他のエラー
            db.session.rollback()
            logger.error(f"商品更新中にエラーが発生: {str(e)}", exc_info=True)
            flash(f'更新中にエラーが発生しました: {str(e)}', 'danger')
            return render_template('edit_product.html', product=product, error=str(e))
    
    # GETリクエスト - 編集フォームを表示
    return render_template('edit_product.html', product=product)

@product_bp.route('/delete/<int:id>', methods=['POST'])
def delete_product(id):
    """商品の削除"""
    try:
        product = Product.query.get_or_404(id)
        product_title = product.title
        
        # 関連する購入履歴を確認
        purchases = Purchase.query.filter_by(product_id=id).all()
        if purchases:
            # 関連する購入履歴がある場合は警告を表示
            flash(f'この商品には{len(purchases)}件の購入履歴が関連付けられています。先に購入履歴を削除してください。', 'warning')
            return redirect(url_for('product.product_detail', id=id))
        
        db.session.delete(product)
        db.session.commit()
        
        flash(f'商品「{product_title}」を削除しました', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"商品削除中にエラーが発生: {str(e)}", exc_info=True)
        flash(f'削除中にエラーが発生しました: {str(e)}', 'danger')
    
    return redirect(url_for('product.product_list'))