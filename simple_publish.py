#!/usr/bin/env python3
"""
シンプルな画像付き記事投稿スクリプト
"""

import logging
import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.publishers.wordpress_client import WordPressClient

def setup_logging():
    """ログ設定"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def simple_publish():
    """シンプルな記事投稿"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 設定とクライアントを初期化
        config = Config()
        wp_client = WordPressClient(config)
        
        # 最新の記事データを読み込み
        article_file = "generated_bitcoin_ath_article_with_images_20250713_235220.json"
        
        with open(article_file, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
        
        # 記事データをシンプル化
        simple_article = {
            'title': article_data.get('title', ''),
            'content': article_data.get('content', ''),
            'category': article_data.get('category', ''),
            'tags': article_data.get('tags', []),
            'article_type': article_data.get('article_type', ''),
            'importance_score': article_data.get('importance_score', 0),
            'word_count': article_data.get('word_count', 0),
            'featured_media': 874  # アップロード済みのアイキャッチ画像ID
        }
        
        logger.info(f"記事投稿開始: {simple_article['title']}")
        
        # 記事を投稿
        result = wp_client.publish_article(simple_article)
        
        if result and result.get('success'):
            print("WordPress投稿成功!")
            print(f"投稿ID: {result.get('id')}")
            print(f"URL: {result.get('url')}")
            print(f"文字数: {simple_article['word_count']:,}文字")
            
            # 成功ログ
            logger.info(f"投稿成功 - ID: {result.get('id')}, URL: {result.get('url')}")
            
        else:
            print("WordPress投稿に失敗しました")
            logger.error("投稿失敗")
        
    except Exception as e:
        print(f"エラー: {e}")
        logger.error(f"投稿エラー: {e}")

if __name__ == "__main__":
    simple_publish()