#!/usr/bin/env python3
"""
記事のアイキャッチ画像を設定
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

def set_featured_image():
    """アイキャッチ画像を設定"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 設定とクライアントを初期化
        config = Config()
        wp_client = WordPressClient(config)
        
        # 記事ID 883のアイキャッチ画像を設定
        post_id = 883
        featured_media_id = 874  # featured_20250713_234914.jpg
        
        logger.info(f"記事ID {post_id} にアイキャッチ画像ID {featured_media_id} を設定中...")
        
        # アイキャッチ画像を設定
        update_data = {
            'featured_media': featured_media_id
        }
        
        result = wp_client._make_request('POST', f'posts/{post_id}', update_data)
        
        if result:
            print("アイキャッチ画像設定成功!")
            print(f"記事ID: {post_id}")
            print(f"アイキャッチ画像ID: {featured_media_id}")
            print(f"画像URL: https://crypto-dictionary.net/wp-content/uploads/2025/07/featured_20250713_234914.jpg")
            
            # 確認のため記事情報を取得
            post_info = wp_client._make_request('GET', f'posts/{post_id}')
            if post_info:
                current_featured = post_info.get('featured_media', 0)
                print(f"確認: 現在のアイキャッチ画像ID = {current_featured}")
                
                if current_featured == featured_media_id:
                    print("✅ アイキャッチ画像が正しく設定されました！")
                else:
                    print("⚠️ アイキャッチ画像の設定を確認してください")
            
        else:
            print("❌ アイキャッチ画像設定に失敗しました")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        logger.error(f"アイキャッチ設定エラー: {e}")

if __name__ == "__main__":
    set_featured_image()