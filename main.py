#!/usr/bin/env python3
"""
仮想通貨メディア自動記事生成システム
メインスクリプト
"""

import logging
import schedule
import time
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.database.db_manager import DatabaseManager
from src.collectors.api_client import CryptoAPIClient
from src.collectors.rss_parser import RSSParser
from src.generators.claude_generator import ClaudeGenerator
from src.publishers.wordpress_client import WordPressClient

def setup_logging():
    """ログ設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/crypto_media.log'),
            logging.StreamHandler()
        ]
    )

def generate_weekly_summary():
    """週刊まとめ記事生成"""
    logger = logging.getLogger(__name__)
    logger.info("週刊まとめ記事生成を開始")
    
    try:
        config = Config()
        db_manager = DatabaseManager(config.DB_PATH)
        api_client = CryptoAPIClient(config)
        rss_parser = RSSParser(config)
        generator = ClaudeGenerator(config)
        wp_client = WordPressClient(config)
        
        # ニュース収集
        news_data = rss_parser.collect_weekly_news()
        crypto_data = api_client.get_market_data()
        
        # 記事生成
        article = generator.generate_weekly_summary(news_data, crypto_data)
        
        # WordPress投稿
        result = wp_client.publish_article(article)
        
        # データベース保存
        db_manager.save_article(article, result)
        
        logger.info("週刊まとめ記事生成完了")
        
    except Exception as e:
        logger.error(f"週刊まとめ記事生成エラー: {e}")

def generate_daily_news():
    """日次ニュース記事生成"""
    logger = logging.getLogger(__name__)
    logger.info("日次ニュース記事生成を開始")
    
    try:
        config = Config()
        db_manager = DatabaseManager(config.DB_PATH)
        rss_parser = RSSParser(config)
        generator = ClaudeGenerator(config)
        wp_client = WordPressClient(config)
        
        # 最新ニュース収集
        news_items = rss_parser.collect_latest_news()
        
        # 重要ニュースを選定して記事生成
        for news_item in news_items[:3]:  # 上位3つのニュース
            article = generator.generate_news_article(news_item)
            
            if article:
                result = wp_client.publish_article(article)
                db_manager.save_article(article, result)
        
        logger.info("日次ニュース記事生成完了")
        
    except Exception as e:
        logger.error(f"日次ニュース記事生成エラー: {e}")

def main():
    """メイン処理"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("仮想通貨メディア自動記事生成システム開始")
    
    # スケジュール設定
    schedule.every().monday.at("09:00").do(generate_weekly_summary)
    schedule.every().day.at("10:00").do(generate_daily_news)
    
    # スケジューラー実行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1分ごとにチェック

if __name__ == "__main__":
    main()