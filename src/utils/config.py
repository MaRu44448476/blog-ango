"""
設定管理モジュール
"""

import os
from dotenv import load_dotenv
from typing import List, Dict, Any
import logging

class Config:
    """設定管理クラス"""
    
    def __init__(self, env_file: str = ".env"):
        """
        設定を初期化
        
        Args:
            env_file: 環境変数ファイルのパス
        """
        load_dotenv(env_file)
        self._setup_logging()
        
    def _setup_logging(self):
        """ログ設定"""
        log_level = getattr(logging, self.LOG_LEVEL, logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # API Keys
    @property
    def COINMARKETCAP_API_KEY(self) -> str:
        return os.getenv("COINMARKETCAP_API_KEY", "")
    
    @property
    def COINGECKO_API_KEY(self) -> str:
        return os.getenv("COINGECKO_API_KEY", "")
    
    @property
    def CRYPTOCOMPARE_API_KEY(self) -> str:
        return os.getenv("CRYPTOCOMPARE_API_KEY", "")
    
    @property
    def OPENAI_API_KEY(self) -> str:
        return os.getenv("OPENAI_API_KEY", "")
    
    @property
    def TWITTER_BEARER_TOKEN(self) -> str:
        return os.getenv("TWITTER_BEARER_TOKEN", "")
    
    @property
    def GOOGLE_NEWS_API_KEY(self) -> str:
        return os.getenv("GOOGLE_NEWS_API_KEY", "")
    
    # WordPress settings
    @property
    def WP_URL(self) -> str:
        return os.getenv("WP_URL", "")
    
    @property
    def WP_USERNAME(self) -> str:
        return os.getenv("WP_USERNAME", "")
    
    @property
    def WP_PASSWORD(self) -> str:
        return os.getenv("WP_PASSWORD", "")
    
    # Database
    @property
    def DB_PATH(self) -> str:
        return os.getenv("DB_PATH", "data/crypto_media.db")
    
    # Schedule settings
    @property
    def WEEKLY_SUMMARY_DAY(self) -> str:
        return os.getenv("WEEKLY_SUMMARY_DAY", "Monday")
    
    @property
    def WEEKLY_SUMMARY_TIME(self) -> str:
        return os.getenv("WEEKLY_SUMMARY_TIME", "09:00")
    
    @property
    def DAILY_NEWS_TIME(self) -> str:
        return os.getenv("DAILY_NEWS_TIME", "10:00")
    
    # Content generation settings
    @property
    def MAX_ARTICLES_PER_DAY(self) -> int:
        return int(os.getenv("MAX_ARTICLES_PER_DAY", "5"))
    
    @property
    def ARTICLE_MIN_LENGTH(self) -> int:
        return int(os.getenv("ARTICLE_MIN_LENGTH", "500"))
    
    @property
    def ARTICLE_MAX_LENGTH(self) -> int:
        return int(os.getenv("ARTICLE_MAX_LENGTH", "2000"))
    
    # Rate limiting
    @property
    def API_RATE_LIMIT(self) -> int:
        return int(os.getenv("API_RATE_LIMIT", "60"))
    
    @property
    def OPENAI_RATE_LIMIT(self) -> int:
        return int(os.getenv("OPENAI_RATE_LIMIT", "20"))
    
    # Logging
    @property
    def LOG_LEVEL(self) -> str:
        return os.getenv("LOG_LEVEL", "INFO")
    
    @property
    def LOG_FILE(self) -> str:
        return os.getenv("LOG_FILE", "logs/crypto_media.log")
    
    # RSS feeds
    @property
    def RSS_FEEDS(self) -> Dict[str, str]:
        return {
            "coindesk": os.getenv("RSS_FEEDS_COINDESK", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
            "cointelegraph": os.getenv("RSS_FEEDS_COINTELEGRAPH", "https://cointelegraph.com/rss"),
            "decrypt": os.getenv("RSS_FEEDS_DECRYPT", "https://decrypt.co/feed"),
            "coinbureau": os.getenv("RSS_FEEDS_COINBUREAU", "https://www.coinbureau.com/feed/")
        }
    
    # Language settings
    @property
    def CONTENT_LANGUAGE(self) -> str:
        return os.getenv("CONTENT_LANGUAGE", "ja")
    
    @property
    def TARGET_AUDIENCE(self) -> str:
        return os.getenv("TARGET_AUDIENCE", "general")
    
    # API endpoints
    @property
    def COINMARKETCAP_BASE_URL(self) -> str:
        return "https://pro-api.coinmarketcap.com/v1"
    
    @property
    def COINGECKO_BASE_URL(self) -> str:
        return "https://api.coingecko.com/api/v3"
    
    @property
    def CRYPTOCOMPARE_BASE_URL(self) -> str:
        return "https://min-api.cryptocompare.com/data"
    
    def validate_config(self) -> bool:
        """
        設定の検証（ClaudeCode環境用）
        
        Returns:
            bool: 設定が有効かどうか
        """
        # ClaudeCode環境では OpenAI API は不要
        required_keys = [
            "WP_URL",
            "WP_USERNAME", 
            "WP_PASSWORD"
        ]
        
        missing_keys = []
        for key in required_keys:
            if not getattr(self, key):
                missing_keys.append(key)
        
        if missing_keys:
            logging.error(f"必須設定が不足しています: {missing_keys}")
            logging.info("WordPress REST API設定について詳細は WORDPRESS_SETUP.md を参照してください")
            return False
        
        return True
    
    def get_article_template_path(self, template_type: str) -> str:
        """
        記事テンプレートパスを取得
        
        Args:
            template_type: テンプレートタイプ
        
        Returns:
            str: テンプレートファイルパス
        """
        return f"templates/{template_type}_template.txt"