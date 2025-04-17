from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import logging
from datetime import datetime, timedelta
from app import db
from app.models.user_settings import UserSettings
from app.utils.dmm_scraper import DmmScraper
from app.utils.dlsite_scraper import DlsiteScraper
from app.models.product import Product
from app.models.purchase import Purchase

# ロガーの設定
logger = logging.getLogger(__name__)

# Blueprintの作成
import_bp = Blueprint('import', __name__, url_prefix='/import')

@import_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    """購入履歴インポート設定ページ"""
    if request.method == 'POST':
        # DMM設定の保存
        dmm_username = request.form.get('dmm_username', '')
        dmm_password = request.form.get('dmm_password', '')
        dmm_enabled = 'dmm_enabled' in request.form
        
        # DLsite設定の保存
        dlsite_username = request.form.get('dlsite_username', '')
        dlsite_password = request.form.get('dlsite_password', '')
        dlsite_enabled = 'dlsite_enabled' in request.form
        
        # 自動インポート設定の保存
        auto_import_interval = request.form.get('auto_import_interval', '0')
        
        # 設定を保存
        if dmm_username:
            UserSettings.set('dmm_username', dmm_username, encrypt=True)
        if dmm_password:
            UserSettings.set('dmm_password', dmm_password, encrypt=True)
        UserSettings.set('dmm_enabled', 'true' if dmm_enabled else 'false')
        
        if dlsite_username:
            UserSettings.set('dlsite_username', dlsite_username, encrypt=True)
        if dlsite_password:
            UserSettings.set('dlsite_password', dlsite_password, encrypt=True)
        UserSettings.set('dlsite_enabled', 'true' if dlsite_enabled else 'false')
        
        UserSettings.set('auto_import_interval', auto_import_interval)
        
        flash('設定が保存されました。', 'success')
        return redirect(url_for('import.settings'))
    
    # 現在の設定を取得
    dmm_username = UserSettings.get('dmm_username', '')
    dmm_enabled = UserSettings.get('dmm_enabled', 'false') == 'true'
    
    dlsite_username = UserSettings.get('dlsite_username', '')
    dlsite_enabled = UserSettings.get('dlsite_enabled', 'false') == 'true'
    
    auto_import_interval = int(UserSettings.get('auto_import_interval', '0'))
    
    # マスク化したユーザー名を表示（セキュリティのため）
    if dmm_username:
        dmm_username_display = dmm_username[:2] + '*' * (len(dmm_username) - 2) if len(dmm_username) > 2 else '**'
    else:
        dmm_username_display = ''
        
    if dlsite_username:
        dlsite_username_display = dlsite_username[:2] + '*' * (len(dlsite_username) - 2) if len(dlsite_username) > 2 else '**'
    else:
        dlsite_username_display = ''
    
    return render_template('import_settings.html',
                           dmm_username=dmm_username_display,
                           dmm_enabled=dmm_enabled,
                           dlsite_username=dlsite_username_display,
                           dlsite_enabled=dlsite_enabled,
                           auto_import_interval=auto_import_interval)

@import_bp.route('/run', methods=['GET', 'POST'])
def run_import():
    """購入履歴のインポート実行"""
    errors = []
    dmm_results = {'added': 0, 'updated': 0, 'errors': []}
    dlsite_results = {'added': 0, 'updated': 0, 'errors': []}
    
    # フォームからのパラメータ取得
    if request.method == 'POST':
        import_dmm = 'import_dmm' in request.form
        import_dlsite = 'import_dlsite' in request.form
        
        start_date = request.form.get('start_date', '')
        end_date = request.form.get('end_date', '')
        max_pages = int(request.form.get('max_pages', '5'))
        
        # DMMからインポート
        if import_dmm:
            dmm_results = import_from_dmm(start_date, end_date, max_pages)
            
        # DLsiteからインポート
        if import_dlsite:
            dlsite_results = import_from_dlsite(start_date, end_date, max_pages)
        
        # 結果を集計
        total_added = dmm_results['added'] + dlsite_results['added']
        total_updated = dmm_results['updated'] + dlsite_results['updated']
        all_errors = dmm_results['errors'] + dlsite_results['errors']
        
        if total_added > 0 or total_updated > 0:
            flash(f'インポートが完了しました。新規追加: {total_added}件、更新: {total_updated}件', 'success')
        
        if all_errors:
            for error in all_errors:
                flash(error, 'danger')
                
    # 設定状態を確認
    dmm_enabled = UserSettings.get('dmm_enabled', 'false') == 'true'
    dmm_username = UserSettings.get('dmm_username', '')
    dmm_has_credentials = bool(dmm_username) and bool(UserSettings.get('dmm_password', ''))
    
    dlsite_enabled = UserSettings.get('dlsite_enabled', 'false') == 'true'
    dlsite_username = UserSettings.get('dlsite_username', '')
    dlsite_has_credentials = bool(dlsite_username) and bool(UserSettings.get('dlsite_password', ''))
    
    # デフォルトの日付範囲（3ヶ月前から今日まで）
    today = datetime.now().date()
    three_months_ago = today - timedelta(days=90)
    
    return render_template('import_run.html',
                           dmm_enabled=dmm_enabled,
                           dmm_has_credentials=dmm_has_credentials,
                           dlsite_enabled=dlsite_enabled,
                           dlsite_has_credentials=dlsite_has_credentials,
                           default_start_date=three_months_ago.isoformat(),
                           default_end_date=today.isoformat(),
                           dmm_results=dmm_results,
                           dlsite_results=dlsite_results)

def import_from_dmm(start_date, end_date, max_pages):
    """DMMから購入履歴をインポート"""
    result = {'added': 0, 'updated': 0, 'errors': []}
    
    # 認証情報を取得
    credentials = UserSettings.get_platform_credentials('dmm')
    if not credentials:
        result['errors'].append('DMMの認証情報が設定されていません。')
        return result
    
    try:
        # DMMにログイン
        scraper = DmmScraper()
        if not scraper.authenticate(credentials['username'], credentials['password']):
            result['errors'].append('DMMへのログインに失敗しました。ユーザー名とパスワードを確認してください。')
            return result
        
        # 購入履歴を取得
        purchase_history = scraper.get_purchase_history(
            start_date=start_date,
            end_date=end_date,
            max_pages=max_pages
        )
        
        if not purchase_history:
            result['errors'].append('DMMから購入履歴が見つかりませんでした。')
            return result
        
        # 購入履歴をデータベースに登録
        for purchase_data in purchase_history:
            try:
                platform_id = purchase_data.get('platform_id')
                if not platform_id:
                    result['errors'].append(f"{purchase_data.get('title', '不明な商品')}のプラットフォームIDが見つかりません")
                    continue
                
                # 既存の商品を検索
                product = Product.query.filter_by(
                    platform='dmm',
                    platform_id=platform_id
                ).first()
                
                # 商品が存在しない場合は新規作成
                if not product:
                    product = Product(
                        platform='dmm',
                        platform_id=platform_id,
                        title=purchase_data.get('title', '不明な商品'),
                        maker=purchase_data.get('maker'),
                        price=purchase_data.get('price'),
                        url=purchase_data.get('url')
                    )
                    db.session.add(product)
                    db.session.flush()  # IDを生成するためにflush
                
                # 購入データの確認
                purchase_date = purchase_data.get('purchase_date')
                if purchase_date:
                    purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                
                # 既存の購入履歴を検索
                existing_purchase = Purchase.query.filter_by(
                    product_id=product.id
                ).first()
                
                if existing_purchase:
                    # 既存の購入履歴がある場合は更新
                    existing_purchase.purchased_date = purchase_date
                    existing_purchase.purchased_price = purchase_data.get('price')
                    db.session.add(existing_purchase)
                    result['updated'] += 1
                else:
                    # 新規購入履歴の作成
                    new_purchase = Purchase(
                        product_id=product.id,
                        purchased_date=purchase_date,
                        purchased_price=purchase_data.get('price'),
                        purchase_type='自動インポート'
                    )
                    db.session.add(new_purchase)
                    result['added'] += 1
                
                # 変更をコミット
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                error_msg = f"{purchase_data.get('title', '不明な商品')}の処理中にエラーが発生しました: {str(e)}"
                logger.error(error_msg)
                result['errors'].append(error_msg)
        
    except Exception as e:
        logger.error(f"DMMからのインポート中にエラーが発生しました: {e}")
        result['errors'].append(f"インポート中にエラーが発生しました: {str(e)}")
    
    return result

def import_from_dlsite(start_date, end_date, max_pages):
    """DLsiteから購入履歴をインポート"""
    result = {'added': 0, 'updated': 0, 'errors': []}
    
    # 認証情報を取得
    credentials = UserSettings.get_platform_credentials('dlsite')
    if not credentials:
        result['errors'].append('DLsiteの認証情報が設定されていません。')
        return result
    
    try:
        # DLsiteにログイン
        scraper = DlsiteScraper()
        if not scraper.authenticate(credentials['username'], credentials['password']):
            result['errors'].append('DLsiteへのログインに失敗しました。ユーザー名とパスワードを確認してください。')
            return result
        
        # 購入履歴を取得
        purchase_history = scraper.get_purchase_history(
            start_date=start_date,
            end_date=end_date,
            max_pages=max_pages
        )
        
        if not purchase_history:
            result['errors'].append('DLsiteから購入履歴が見つかりませんでした。')
            return result
        
        # 購入履歴をデータベースに登録
        for purchase_data in purchase_history:
            try:
                platform_id = purchase_data.get('platform_id')
                if not platform_id:
                    result['errors'].append(f"{purchase_data.get('title', '不明な商品')}のプラットフォームIDが見つかりません")
                    continue
                
                # 既存の商品を検索
                product = Product.query.filter_by(
                    platform='dlsite',
                    platform_id=platform_id
                ).first()
                
                # 商品が存在しない場合は新規作成
                if not product:
                    product = Product(
                        platform='dlsite',
                        platform_id=platform_id,
                        title=purchase_data.get('title', '不明な商品'),
                        maker=purchase_data.get('maker'),
                        price=purchase_data.get('price'),
                        url=purchase_data.get('url')
                    )
                    db.session.add(product)
                    db.session.flush()  # IDを生成するためにflush
                
                # 購入データの確認
                purchase_date = purchase_data.get('purchase_date')
                if purchase_date:
                    purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()
                
                # 既存の購入履歴を検索
                existing_purchase = Purchase.query.filter_by(
                    product_id=product.id
                ).first()
                
                if existing_purchase:
                    # 既存の購入履歴がある場合は更新
                    existing_purchase.purchased_date = purchase_date
                    existing_purchase.purchased_price = purchase_data.get('price')
                    db.session.add(existing_purchase)
                    result['updated'] += 1
                else:
                    # 新規購入履歴の作成
                    new_purchase = Purchase(
                        product_id=product.id,
                        purchased_date=purchase_date,
                        purchased_price=purchase_data.get('price'),
                        purchase_type='自動インポート'
                    )
                    db.session.add(new_purchase)
                    result['added'] += 1
                
                # 変更をコミット
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                error_msg = f"{purchase_data.get('title', '不明な商品')}の処理中にエラーが発生しました: {str(e)}"
                logger.error(error_msg)
                result['errors'].append(error_msg)
        
    except Exception as e:
        logger.error(f"DLsiteからのインポート中にエラーが発生しました: {e}")
        result['errors'].append(f"インポート中にエラーが発生しました: {str(e)}")
    
    return result

@import_bp.route('/api/test-connection', methods=['POST'])
def test_connection():
    """APIエンドポイント: 接続テスト"""
    platform = request.json.get('platform', '')
    username = request.json.get('username', '')
    password = request.json.get('password', '')
    
    if not platform or not username or not password:
        return jsonify({
            'success': False,
            'message': '必要なパラメータが不足しています'
        }), 400
    
    try:
        if platform == 'dmm':
            scraper = DmmScraper()
        elif platform == 'dlsite':
            scraper = DlsiteScraper()
        else:
            return jsonify({
                'success': False,
                'message': '無効なプラットフォームです'
            }), 400
        
        # ログインテスト
        success = scraper.authenticate(username, password)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'{platform.upper()}への接続テストに成功しました'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'{platform.upper()}への接続に失敗しました。ユーザー名とパスワードを確認してください'
            })
            
    except Exception as e:
        logger.error(f"接続テスト中にエラーが発生: {e}")
        return jsonify({
            'success': False,
            'message': f'エラーが発生しました: {str(e)}'
        }), 500