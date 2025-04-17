#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import threading
import logging
from logging.handlers import RotatingFileHandler
from app import create_app

# ロギング設定
if not os.path.exists('logs'):
    os.makedirs('logs')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=5),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def install_playwright_browsers():
    """Playwrightの必要なブラウザをインストールする"""
    try:
        logger.info("Playwrightブラウザのインストールを開始します...")
        subprocess.run(["playwright", "install", "chromium"], check=True)
        logger.info("Playwrightブラウザのインストールが完了しました")
    except Exception as e:
        logger.error(f"Playwrightブラウザのインストール中にエラーが発生しました: {e}")
        logger.info("手動でインストールする場合は、コマンドラインで 'playwright install chromium' を実行してください")

# Playwrightブラウザのインストール（別スレッドで実行して起動時間を短縮）
threading.Thread(target=install_playwright_browsers).start()

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)