from datetime import datetime
from app import db

class WatchlistItem(db.Model):
    """購入予定リストモデル - 購入検討中の商品を管理"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    target_price = db.Column(db.Integer)  # この価格以下になったら通知
    priority = db.Column(db.Integer, default=0)  # 優先度（1: 低 - 5: 高）
    note = db.Column(db.Text)  # メモ
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 商品との関連付け
    product = db.relationship('Product', backref=db.backref('watchlist_items', lazy=True))
    
    def __repr__(self):
        return f'<WatchlistItem {self.id} for Product:{self.product_id}>'
    
    def to_dict(self):
        """ウォッチリスト情報を辞書形式で返す"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'target_price': self.target_price,
            'priority': self.priority,
            'note': self.note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }