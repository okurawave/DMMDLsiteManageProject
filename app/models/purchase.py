from datetime import datetime
from app import db

class Purchase(db.Model):
    """購入履歴モデル - ユーザーの購入情報を管理"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    purchased_date = db.Column(db.Date, nullable=False)  # 購入日
    purchased_price = db.Column(db.Integer)  # 購入時の価格
    purchase_type = db.Column(db.String(50))  # 通常購入、セール購入など
    note = db.Column(db.Text)  # 備考
    created_at = db.Column(db.DateTime, default=datetime.now)  # 作成日時
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 更新日時
    
    def __repr__(self):
        return f'<Purchase {self.id} Product:{self.product_id} Date:{self.purchased_date}>'
    
    def to_dict(self):
        """購入履歴情報を辞書形式で返す"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'purchased_date': self.purchased_date.strftime('%Y-%m-%d'),
            'purchased_price': self.purchased_price,
            'purchase_type': self.purchase_type,
            'note': self.note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }