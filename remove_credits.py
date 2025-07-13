#!/usr/bin/env python3
"""
記事下部のクレジット表記を削除
"""

import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.publishers.wordpress_client import WordPressClient

def setup_logging():
    """ログ設定"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def remove_credits():
    """記事からクレジット表記を削除"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 設定とクライアントを初期化
        config = Config()
        wp_client = WordPressClient(config)
        
        # 記事ID 883の内容を取得
        post_id = 883
        
        logger.info(f"記事ID {post_id} の内容を取得中...")
        
        post_info = wp_client._make_request('GET', f'posts/{post_id}')
        
        if not post_info:
            print("記事の取得に失敗しました")
            return
        
        current_content = post_info.get('content', {}).get('rendered', '')
        
        # クレジット表記を削除
        updated_content = current_content
        
        # 削除対象のパターン
        credit_patterns = [
            '<hr>\n<p><small>🤖 Generated with Claude Code | 🎨 Powered by OpenAI DALL-E 3</small></p>',
            '<hr><p><small>🤖 Generated with Claude Code | 🎨 Powered by OpenAI DALL-E 3</small></p>',
            '<p><small>🤖 Generated with Claude Code | 🎨 Powered by OpenAI DALL-E 3</small></p>',
            '🤖 Generated with Claude Code | 🎨 Powered by OpenAI DALL-E 3',
            '<hr>',  # 最後のhrタグも削除
        ]
        
        # パターンごとに削除
        for pattern in credit_patterns:
            updated_content = updated_content.replace(pattern, '')
        
        # 末尾の空白や改行を整理
        updated_content = updated_content.strip()
        
        # 記事を更新
        update_data = {
            'content': updated_content
        }
        
        logger.info("クレジット表記を削除して記事を更新中...")
        
        result = wp_client._make_request('POST', f'posts/{post_id}', update_data)
        
        if result:
            print("クレジット表記削除完了!")
            print(f"記事ID: {post_id}")
            print("記事末尾のクレジット表記が削除されました")
            print("記事をリロードして確認してください")
            
        else:
            print("記事更新に失敗しました")
        
    except Exception as e:
        print(f"エラー: {e}")
        logger.error(f"クレジット削除エラー: {e}")

if __name__ == "__main__":
    remove_credits()