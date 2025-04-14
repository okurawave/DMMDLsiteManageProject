from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# データベース初期化
db = SQLAlchemy()
migrate = Migrate()

def create_app(config=None):
    # Flaskアプリケーションの初期化
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///products.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # データベースの初期化
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Blueprintsの登録
    from app.controllers.main_controller import main_bp
    from app.controllers.scraper_controller import scraper_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(scraper_bp)
    
    # エラーハンドラの登録
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_code=404, error_message='ページが見つかりません'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('error.html', error_code=500, error_message='サーバーエラーが発生しました'), 500
    
    # コンテキストプロセッサ（すべてのテンプレートで利用可能な変数）
    @app.context_processor
    def utility_processor():
        return {
            'app_name': 'DMM/DLsite 購入管理',
            'app_version': '2.0.0'  # フェーズ2のバージョン
        }
    
    # データベース作成
    with app.app_context():
        db.create_all()
    
    return app