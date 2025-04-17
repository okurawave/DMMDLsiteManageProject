#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import db
from datetime import datetime
import json
from cryptography.fernet import Fernet
import os
import base64

# 暗号化キーの生成・取得
def get_encryption_key():
    key_path = "config/encryption_key.key"
    if os.path.exists(key_path):
        with open(key_path, 'rb') as f:
            key = f.read()
    else:
        # キーが存在しない場合は新規生成し保存
        key = Fernet.generate_key()
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        with open(key_path, 'wb') as f:
            f.write(key)
    return key

# 暗号化用のFernetインスタンスを生成
try:
    ENCRYPTION_KEY = get_encryption_key()
    cipher_suite = Fernet(ENCRYPTION_KEY)
except Exception as e:
    print(f"暗号化キーの準備に失敗しました: {e}")
    # フォールバックとして一時的なキーを使用（再起動すると変わるので注意）
    cipher_suite = Fernet(Fernet.generate_key())

class UserSettings(db.Model):
    """ユーザー設定モデル"""
    
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)
    value = db.Column(db.Text)
    encrypted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    @classmethod
    def get(cls, key, default=None):
        """設定値を取得"""
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            return default
            
        if setting.encrypted:
            try:
                # 暗号化された値を復号
                decrypted = cipher_suite.decrypt(setting.value.encode())
                return decrypted.decode()
            except Exception as e:
                print(f"設定値の復号に失敗しました（{key}）: {e}")
                return default
        else:
            return setting.value
    
    @classmethod
    def set(cls, key, value, encrypt=False):
        """設定値を保存"""
        setting = cls.query.filter_by(key=key).first()
        
        if not setting:
            setting = cls(key=key)
        
        if encrypt:
            # 値を暗号化して保存
            encrypted = cipher_suite.encrypt(str(value).encode())
            setting.value = encrypted.decode()
            setting.encrypted = True
        else:
            setting.value = str(value)
            setting.encrypted = False
        
        db.session.add(setting)
        db.session.commit()
        return setting
    
    @classmethod
    def delete(cls, key):
        """設定値を削除"""
        setting = cls.query.filter_by(key=key).first()
        if setting:
            db.session.delete(setting)
            db.session.commit()
            return True
        return False
    
    @classmethod
    def get_platform_credentials(cls, platform):
        """特定のプラットフォームの認証情報を取得"""
        username = cls.get(f"{platform}_username")
        password = cls.get(f"{platform}_password")
        
        if username and password:
            return {
                'username': username,
                'password': password
            }
        return None