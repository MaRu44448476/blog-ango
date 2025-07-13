#!/usr/bin/env python3
"""
システムテストスクリプト
"""

import sys
import os
import logging
from datetime import datetime

# プロジェクトのルートディレクトリをPythonパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.database.db_manager import DatabaseManager
from src.collectors.api_client import CryptoAPIClient
from src.collectors.rss_parser import RSSParser
from src.generators.weekly_summary import WeeklySummaryGenerator
from src.generators.news_writer import NewsWriter
from src.publishers.wordpress_client import WordPressClient

def setup_logging():
    """ログ設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_config():
    """設定テスト"""
    print("🔧 設定テスト中...")
    try:
        config = Config()
        if config.validate_config():
            print("✅ 設定は有効です")
            return True
        else:
            print("❌ 設定に問題があります")
            return False
    except Exception as e:
        print(f"❌ 設定エラー: {e}")
        return False

def test_database():
    """データベーステスト"""
    print("\n🗄️ データベーステスト中...")
    try:
        config = Config()
        db_manager = DatabaseManager(config.DB_PATH)
        
        # テストデータを挿入
        test_news = [{
            'title': 'テストニュース',
            'url': 'https://example.com/test',
            'content': 'これはテスト用のニュースです',
            'source': 'test',
            'importance_score': 50
        }]
        
        saved_count = db_manager.save_news_data(test_news)
        if saved_count > 0:
            print("✅ データベース接続成功")
            return True
        else:
            print("⚠️ データベースに保存できませんでした")
            return False
            
    except Exception as e:
        print(f"❌ データベースエラー: {e}")
        return False

def test_api_clients():
    """APIクライアントテスト"""
    print("\n📊 APIクライアントテスト中...")
    try:
        config = Config()
        api_client = CryptoAPIClient(config)
        
        # CoinGeckoデータを取得
        market_data = api_client.get_coingecko_market_data(limit=5)
        
        if market_data and len(market_data) > 0:
            print(f"✅ CoinGecko API接続成功 ({len(market_data)}件のデータを取得)")
            print(f"   サンプル: {market_data[0].get('symbol')} - ${market_data[0].get('price', 0):,.2f}")
            return True
        else:
            print("⚠️ CoinGecko APIからデータを取得できませんでした")
            return False
            
    except Exception as e:
        print(f"❌ APIクライアントエラー: {e}")
        return False

def test_rss_parser():
    """RSSパーサーテスト"""
    print("\n📰 RSSパーサーテスト中...")
    try:
        config = Config()
        rss_parser = RSSParser(config)
        
        # 1つのフィードをテスト
        news_items = rss_parser.collect_latest_news(hours=24)
        
        if news_items and len(news_items) > 0:
            print(f"✅ RSSパーサー動作確認 ({len(news_items)}件のニュースを取得)")
            print(f"   サンプル: {news_items[0].get('title', '')[:50]}...")
            return True
        else:
            print("⚠️ RSSフィードからニュースを取得できませんでした")
            return False
            
    except Exception as e:
        print(f"❌ RSSパーサーエラー: {e}")
        return False

def test_content_generation():
    """コンテンツ生成テスト"""
    print("\n✍️ コンテンツ生成テスト中...")
    try:
        config = Config()
        
        if not config.OPENAI_API_KEY:
            print("⚠️ OpenAI APIキーが設定されていません")
            return False
        
        # テスト用のニュースデータ
        test_news = [{
            'title': 'ビットコイン価格が新高値を更新',
            'content': 'ビットコインの価格が過去最高値を更新し、市場に注目が集まっています。',
            'source': 'test',
            'importance_score': 80
        }]
        
        news_writer = NewsWriter(config)
        article = news_writer.generate_news_article(test_news[0])
        
        if article and article.get('title') and article.get('content'):
            print(f"✅ コンテンツ生成成功 ({article.get('word_count', 0)}字)")
            print(f"   タイトル: {article.get('title', '')[:50]}...")
            return True
        else:
            print("❌ コンテンツ生成に失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ コンテンツ生成エラー: {e}")
        return False

def test_wordpress_connection():
    """WordPress接続テスト"""
    print("\n🌐 WordPress接続テスト中...")
    try:
        config = Config()
        
        if not all([config.WP_URL, config.WP_USERNAME, config.WP_PASSWORD]):
            print("⚠️ WordPress設定が不完全です")
            return False
        
        wp_client = WordPressClient(config)
        
        if wp_client.test_connection():
            print("✅ WordPress接続成功")
            return True
        else:
            print("❌ WordPress接続に失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ WordPress接続エラー: {e}")
        return False

def test_full_workflow():
    """フルワークフローテスト"""
    print("\n🔄 フルワークフローテスト中...")
    try:
        config = Config()
        
        # 1. データ収集
        api_client = CryptoAPIClient(config)
        market_data = api_client.get_coingecko_market_data(limit=3)
        
        rss_parser = RSSParser(config)
        news_data = rss_parser.collect_latest_news(hours=48)[:3]
        
        if not news_data:
            print("⚠️ テスト用ニュースデータが不足しています")
            return False
        
        # 2. データベース保存
        db_manager = DatabaseManager(config.DB_PATH)
        db_manager.save_news_data(news_data)
        db_manager.save_market_data(market_data)
        
        # 3. 記事生成（OpenAI APIキーが必要）
        if config.OPENAI_API_KEY:
            news_writer = NewsWriter(config)
            article = news_writer.generate_news_article(news_data[0])
            
            if article:
                # 4. データベースに記事保存
                article_id = db_manager.save_article(article)
                print(f"✅ フルワークフロー成功 (記事ID: {article_id})")
                return True
            else:
                print("❌ 記事生成に失敗しました")
                return False
        else:
            print("⚠️ OpenAI APIキーが設定されていないため、記事生成をスキップ")
            print("✅ フルワークフロー（記事生成以外）成功")
            return True
            
    except Exception as e:
        print(f"❌ フルワークフローエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    setup_logging()
    
    print("🚀 仮想通貨メディア自動記事生成システム テスト開始")
    print("=" * 60)
    
    test_results = []
    
    # 各テストを実行
    test_results.append(("設定テスト", test_config()))
    test_results.append(("データベーステスト", test_database()))
    test_results.append(("APIクライアントテスト", test_api_clients()))
    test_results.append(("RSSパーサーテスト", test_rss_parser()))
    test_results.append(("コンテンツ生成テスト", test_content_generation()))
    test_results.append(("WordPress接続テスト", test_wordpress_connection()))
    test_results.append(("フルワークフローテスト", test_full_workflow()))
    
    # 結果をまとめて表示
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"総合結果: {passed}/{total} テスト通過")
    
    if passed == total:
        print("🎉 すべてのテストが通過しました！システムは正常に動作しています。")
        return 0
    else:
        print("⚠️ 一部のテストが失敗しました。設定を確認してください。")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)