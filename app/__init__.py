from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# データベースのインスタンスを作成
db = SQLAlchemy()

def create_app():
    """アプリケーションファクトリ関数"""
    app = Flask(__name__)
    
    # データベース設定
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'products.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'dmm-dlsite-compare-secret-key'
    
    # データベースを初期化
    db.init_app(app)
    
    # コントローラーを登録
    from app.controllers.main_controller import main_bp
    app.register_blueprint(main_bp)
    
    # データベーステーブルの作成
    with app.app_context():
        db.create_all()
    
    return app