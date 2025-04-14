from datetime import datetime
from app import db

class Product(db.Model):
    """商品モデル - DMMとDLsiteの商品情報を管理"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)  # 商品タイトル
    platform = db.Column(db.String(10), nullable=False)  # 'dmm'または'dlsite'
    platform_id = db.Column(db.String(50), nullable=False)  # 各プラットフォームでの商品ID
    url = db.Column(db.String(512))  # 商品URL
    price = db.Column(db.Integer)  # 価格
    discount_price = db.Column(db.Integer)  # セール価格（あれば）
    maker = db.Column(db.String(255))  # メーカー/サークル名
    release_date = db.Column(db.Date)  # 発売日
    thumbnail_url = db.Column(db.String(512))  # サムネイル画像URL
    category = db.Column(db.String(100))  # カテゴリ
    last_updated = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 最終更新日時
    
    # platformとplatform_idのユニーク制約を設定
    __table_args__ = (
        db.UniqueConstraint('platform', 'platform_id'),
    )
    
    # 購入履歴との関連付け
    purchases = db.relationship('Purchase', backref='product', lazy=True)
    
    def __repr__(self):
        return f'<Product {self.platform}:{self.platform_id} {self.title}>'
    
    def to_dict(self):
        """商品情報を辞書形式で返す"""
        return {
            'id': self.id,
            'title': self.title,
            'platform': self.platform,
            'platform_id': self.platform_id,
            'url': self.url,
            'price': self.price,
            'discount_price': self.discount_price,
            'maker': self.maker,
            'release_date': self.release_date.strftime('%Y-%m-%d') if self.release_date else None,
            'thumbnail_url': self.thumbnail_url,
            'category': self.category,
            'last_updated': self.last_updated.strftime('%Y-%m-%d %H:%M:%S')
        }

    @staticmethod
    def find_duplicates():
        """タイトルとメーカーから重複している可能性のある商品を検索"""
        # 実装はフェーズ2で詳細化
        pass