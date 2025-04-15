from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.product import Product
from app.models.purchase import Purchase
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

# Blueprintの作成
purchase_bp = Blueprint('purchase', __name__, url_prefix='/purchase')

@purchase_bp.route('/')
def purchase_list():
    """購入履歴リストを表示"""
    # クエリパラメータからフィルタ条件を取得
    platform = request.args.get('platform', '')
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'purchased_date')
    sort_dir = request.args.get('dir', 'desc')  # デフォルトは降順（新しい順）
    
    # ベースクエリを作成 - Purchaseモデルと関連するProductモデルを結合
    query = db.session.query(Purchase, Product).join(Product, Purchase.product_id == Product.id)
    
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
        order_col = Purchase.purchased_price
    elif sort_by == 'title':
        order_col = Product.title
    elif sort_by == 'platform':
        order_col = Product.platform
    else:  # デフォルトは購入日順
        order_col = Purchase.purchased_date
    
    if sort_dir == 'asc':
        order_col = order_col.asc()
    else:
        order_col = order_col.desc()
    
    query = query.order_by(order_col)
    
    # ページネーション
    page = request.args.get('page', 1, type=int)
    per_page = 20  # 1ページあたりの表示件数
    
    # ページネーション用にクエリを変換
    purchase_results = query.paginate(page=page, per_page=per_page)
    
    # 統計情報の計算
    total_spent = db.session.query(db.func.sum(Purchase.purchased_price)).scalar() or 0
    total_purchases = Purchase.query.count()
    
    return render_template('purchases.html', 
                          purchases=purchase_results,
                          total_spent=total_spent,
                          total_purchases=total_purchases,
                          platform=platform,
                          search_query=search_query,
                          sort_by=sort_by,
                          sort_dir=sort_dir)

@purchase_bp.route('/add', methods=['GET', 'POST'])
def add_purchase():
    """購入履歴の追加"""
    if request.method == 'POST':
        try:
            # フォームからデータを取得
            product_id = request.form.get('product_id')
            purchase_date_str = request.form.get('purchase_date')
            purchase_price = request.form.get('purchase_price')
            purchase_type = request.form.get('purchase_type', '通常')
            
            # 必須フィールドのバリデーション
            if not product_id:
                raise ValueError('商品を選択してください')
            if not purchase_price:
                raise ValueError('購入価格を入力してください')
            
            # 商品の存在確認
            product = Product.query.get(product_id)
            if not product:
                raise ValueError('選択された商品が存在しません')
            
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
            
            # 既存の購入履歴をチェック
            existing_purchase = Purchase.query.filter_by(product_id=product_id).first()
            if existing_purchase:
                # 同じ商品の購入履歴が既に存在する場合は警告を表示
                flash(f'この商品の購入履歴は既に存在します（ID: {existing_purchase.id}）。重複を避けるため、編集してください。', 'warning')
                return redirect(url_for('product.product_detail', id=product_id))
            
            # 新しい購入履歴を作成
            new_purchase = Purchase(
                product_id=product_id,
                purchased_date=purchase_date,
                purchased_price=purchase_price,
                purchase_type=purchase_type
            )
            
            db.session.add(new_purchase)
            db.session.commit()
            
            flash(f'「{product.title}」の購入情報を追加しました', 'success')
            return redirect(url_for('product.product_detail', id=product_id))
            
        except ValueError as ve:
            # バリデーションエラー
            flash(str(ve), 'danger')
            # 商品リストを取得してフォームを再表示
            products = Product.query.order_by(Product.title).all()
            return render_template('add_purchase.html', 
                                  now=datetime.now(),
                                  products=products,
                                  form_data=request.form,
                                  error=str(ve))
            
        except Exception as e:
            # その他のエラー
            db.session.rollback()
            logger.error(f"購入情報追加中にエラーが発生: {str(e)}", exc_info=True)
            flash(f'エラーが発生しました: {str(e)}', 'danger')
            # 商品リストを取得してフォームを再表示
            products = Product.query.order_by(Product.title).all()
            return render_template('add_purchase.html', 
                                  now=datetime.now(),
                                  products=products,
                                  form_data=request.form,
                                  error=str(e))
    
    # GETリクエスト - フォームを表示
    products = Product.query.order_by(Product.title).all()
    # 製品IDがURLパラメータで指定されている場合は取得
    preselected_product_id = request.args.get('product_id')
    
    return render_template('add_purchase.html', 
                          now=datetime.now(),
                          products=products,
                          preselected_product_id=preselected_product_id)

@purchase_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_purchase(id):
    """購入履歴の編集"""
    purchase = Purchase.query.get_or_404(id)
    product = Product.query.get(purchase.product_id)
    
    if request.method == 'POST':
        try:
            # フォームからデータを取得して更新
            purchase_date_str = request.form.get('purchase_date')
            purchase.purchased_price = request.form.get('purchase_price')
            purchase.purchase_type = request.form.get('purchase_type', '通常')
            
            # 必須フィールドのバリデーション
            if not purchase.purchased_price:
                raise ValueError('購入価格を入力してください')
            
            # 日付の変換
            if purchase_date_str:
                try:
                    purchase.purchased_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"無効な購入日フォーマット: {purchase_date_str}, 更新しません")
            
            db.session.commit()
            
            flash(f'「{product.title}」の購入情報を更新しました', 'success')
            return redirect(url_for('product.product_detail', id=product.id))
            
        except ValueError as ve:
            # バリデーションエラー
            flash(str(ve), 'danger')
            return render_template('edit_purchase.html', purchase=purchase, product=product, error=str(ve))
            
        except Exception as e:
            # その他のエラー
            db.session.rollback()
            logger.error(f"購入情報更新中にエラーが発生: {str(e)}", exc_info=True)
            flash(f'更新中にエラーが発生しました: {str(e)}', 'danger')
            return render_template('edit_purchase.html', purchase=purchase, product=product, error=str(e))
    
    # GETリクエスト - 編集フォームを表示
    return render_template('edit_purchase.html', purchase=purchase, product=product)

@purchase_bp.route('/delete/<int:id>', methods=['POST'])
def delete_purchase(id):
    """購入履歴の削除"""
    try:
        purchase = Purchase.query.get_or_404(id)
        product_id = purchase.product_id
        product = Product.query.get(product_id)
        
        db.session.delete(purchase)
        db.session.commit()
        
        flash(f'「{product.title}」の購入情報を削除しました', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"購入情報削除中にエラーが発生: {str(e)}", exc_info=True)
        flash(f'削除中にエラーが発生しました: {str(e)}', 'danger')
    
    # 商品の詳細ページにリダイレクト
    return redirect(url_for('product.product_detail', id=product_id))