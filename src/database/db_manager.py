"""
データベース管理モジュール
"""

import sqlite3
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

class DatabaseManager:
    """データベース管理クラス"""
    
    def __init__(self, db_path: str):
        """
        データベースマネージャーを初期化
        
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # データベースディレクトリを作成
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # データベースとテーブルを初期化
        self._init_database()
    
    def _init_database(self):
        """データベースとテーブルを初期化"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # ニュースデータテーブル
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS news_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        url TEXT UNIQUE NOT NULL,
                        content TEXT,
                        source TEXT NOT NULL,
                        publish_date DATETIME,
                        collect_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        sentiment_score REAL,
                        importance_score REAL,
                        processed BOOLEAN DEFAULT 0
                    )
                ''')
                
                # 市場データテーブル
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS market_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        symbol TEXT NOT NULL,
                        price REAL NOT NULL,
                        market_cap REAL,
                        volume_24h REAL,
                        price_change_24h REAL,
                        price_change_percentage_24h REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 生成記事テーブル
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS generated_articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        article_type TEXT NOT NULL,
                        category TEXT,
                        tags TEXT,
                        word_count INTEGER,
                        generation_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        published BOOLEAN DEFAULT 0,
                        wp_post_id INTEGER,
                        wp_publish_date DATETIME,
                        source_news_ids TEXT,
                        metadata TEXT
                    )
                ''')
                
                # 投稿履歴テーブル
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS publish_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        article_id INTEGER NOT NULL,
                        wp_post_id INTEGER,
                        publish_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status TEXT NOT NULL,
                        error_message TEXT,
                        FOREIGN KEY (article_id) REFERENCES generated_articles (id)
                    )
                ''')
                
                # API使用状況テーブル
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS api_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_name TEXT NOT NULL,
                        endpoint TEXT,
                        request_count INTEGER DEFAULT 1,
                        date DATE DEFAULT CURRENT_DATE,
                        response_time REAL,
                        status_code INTEGER,
                        error_message TEXT
                    )
                ''')
                
                conn.commit()
                self.logger.info("データベース初期化完了")
                
        except Exception as e:
            self.logger.error(f"データベース初期化エラー: {e}")
            raise
    
    def save_news_data(self, news_items: List[Dict[str, Any]]) -> int:
        """
        ニュースデータを保存
        
        Args:
            news_items: ニュースアイテムのリスト
            
        Returns:
            int: 保存されたアイテム数
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                saved_count = 0
                
                for item in news_items:
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO news_data 
                            (title, url, content, source, publish_date, sentiment_score, importance_score)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            item.get('title', ''),
                            item.get('url', ''),
                            item.get('content', ''),
                            item.get('source', ''),
                            item.get('publish_date'),
                            item.get('sentiment_score'),
                            item.get('importance_score')
                        ))
                        
                        if cursor.rowcount > 0:
                            saved_count += 1
                            
                    except Exception as e:
                        self.logger.warning(f"ニュース保存エラー: {e}")
                        continue
                
                conn.commit()
                self.logger.info(f"ニュースデータ {saved_count}件を保存")
                return saved_count
                
        except Exception as e:
            self.logger.error(f"ニュースデータ保存エラー: {e}")
            return 0
    
    def save_market_data(self, market_data: List[Dict[str, Any]]) -> int:
        """
        市場データを保存
        
        Args:
            market_data: 市場データのリスト
            
        Returns:
            int: 保存されたアイテム数
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                saved_count = 0
                
                for item in market_data:
                    cursor.execute('''
                        INSERT INTO market_data 
                        (symbol, price, market_cap, volume_24h, price_change_24h, price_change_percentage_24h)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('symbol', ''),
                        item.get('price', 0),
                        item.get('market_cap', 0),
                        item.get('volume_24h', 0),
                        item.get('price_change_24h', 0),
                        item.get('price_change_percentage_24h', 0)
                    ))
                    saved_count += 1
                
                conn.commit()
                self.logger.info(f"市場データ {saved_count}件を保存")
                return saved_count
                
        except Exception as e:
            self.logger.error(f"市場データ保存エラー: {e}")
            return 0
    
    def save_article(self, article: Dict[str, Any], wp_result: Optional[Dict[str, Any]] = None) -> int:
        """
        生成記事を保存
        
        Args:
            article: 記事データ
            wp_result: WordPress投稿結果
            
        Returns:
            int: 記事ID
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 記事を保存
                cursor.execute('''
                    INSERT INTO generated_articles 
                    (title, content, article_type, category, tags, word_count, 
                     published, wp_post_id, wp_publish_date, source_news_ids, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article.get('title', ''),
                    article.get('content', ''),
                    article.get('article_type', ''),
                    article.get('category', ''),
                    json.dumps(article.get('tags', [])),
                    article.get('word_count', 0),
                    bool(wp_result),
                    wp_result.get('id') if wp_result else None,
                    wp_result.get('date') if wp_result else None,
                    json.dumps(article.get('source_news_ids', [])),
                    json.dumps(article.get('metadata', {}))
                ))
                
                article_id = cursor.lastrowid
                
                # 投稿履歴を保存
                if wp_result:
                    cursor.execute('''
                        INSERT INTO publish_history 
                        (article_id, wp_post_id, status, error_message)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        article_id,
                        wp_result.get('id'),
                        'success' if wp_result.get('status') == 'publish' else 'error',
                        wp_result.get('error_message')
                    ))
                
                conn.commit()
                self.logger.info(f"記事ID {article_id} を保存")
                return article_id
                
        except Exception as e:
            self.logger.error(f"記事保存エラー: {e}")
            return 0
    
    def get_recent_news(self, days: int = 7, limit: int = 100) -> List[Dict[str, Any]]:
        """
        最近のニュースを取得
        
        Args:
            days: 取得する日数
            limit: 取得する最大件数
            
        Returns:
            List[Dict]: ニュースリスト
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM news_data 
                    WHERE collect_date >= datetime('now', '-{} days')
                    ORDER BY importance_score DESC, collect_date DESC
                    LIMIT ?
                '''.format(days), (limit,))
                
                columns = [desc[0] for desc in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    row_dict = dict(zip(columns, row))
                    results.append(row_dict)
                
                return results
                
        except Exception as e:
            self.logger.error(f"ニュース取得エラー: {e}")
            return []
    
    def get_market_trends(self, symbol: str, hours: int = 24) -> List[Dict[str, Any]]:
        """
        市場トレンドを取得
        
        Args:
            symbol: 通貨シンボル
            hours: 取得する時間数
            
        Returns:
            List[Dict]: 市場データリスト
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM market_data 
                    WHERE symbol = ? AND timestamp >= datetime('now', '-{} hours')
                    ORDER BY timestamp DESC
                '''.format(hours), (symbol,))
                
                columns = [desc[0] for desc in cursor.description]
                results = []
                
                for row in cursor.fetchall():
                    row_dict = dict(zip(columns, row))
                    results.append(row_dict)
                
                return results
                
        except Exception as e:
            self.logger.error(f"市場データ取得エラー: {e}")
            return []
    
    def record_api_usage(self, api_name: str, endpoint: str = None, 
                        response_time: float = None, status_code: int = None,
                        error_message: str = None):
        """
        API使用状況を記録
        
        Args:
            api_name: API名
            endpoint: エンドポイント
            response_time: レスポンス時間
            status_code: ステータスコード
            error_message: エラーメッセージ
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO api_usage 
                    (api_name, endpoint, response_time, status_code, error_message)
                    VALUES (?, ?, ?, ?, ?)
                ''', (api_name, endpoint, response_time, status_code, error_message))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"API使用状況記録エラー: {e}")
    
    def get_daily_stats(self) -> Dict[str, Any]:
        """
        日次統計を取得
        
        Returns:
            Dict: 統計データ
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # 今日収集したニュース数
                cursor.execute('''
                    SELECT COUNT(*) FROM news_data 
                    WHERE date(collect_date) = date('now')
                ''')
                stats['news_collected_today'] = cursor.fetchone()[0]
                
                # 今日生成した記事数
                cursor.execute('''
                    SELECT COUNT(*) FROM generated_articles 
                    WHERE date(generation_date) = date('now')
                ''')
                stats['articles_generated_today'] = cursor.fetchone()[0]
                
                # 今日の投稿数
                cursor.execute('''
                    SELECT COUNT(*) FROM publish_history 
                    WHERE date(publish_date) = date('now') AND status = 'success'
                ''')
                stats['articles_published_today'] = cursor.fetchone()[0]
                
                # API使用状況
                cursor.execute('''
                    SELECT api_name, SUM(request_count) as total_requests
                    FROM api_usage 
                    WHERE date = date('now')
                    GROUP BY api_name
                ''')
                stats['api_usage_today'] = dict(cursor.fetchall())
                
                return stats
                
        except Exception as e:
            self.logger.error(f"統計取得エラー: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 30):
        """
        古いデータをクリーンアップ
        
        Args:
            days: 保持する日数
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 古いニュースデータを削除
                cursor.execute('''
                    DELETE FROM news_data 
                    WHERE collect_date < datetime('now', '-{} days')
                '''.format(days))
                
                # 古い市場データを削除
                cursor.execute('''
                    DELETE FROM market_data 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days))
                
                # 古いAPI使用状況を削除
                cursor.execute('''
                    DELETE FROM api_usage 
                    WHERE date < date('now', '-{} days')
                '''.format(days))
                
                conn.commit()
                self.logger.info(f"{days}日以前のデータをクリーンアップ")
                
        except Exception as e:
            self.logger.error(f"データクリーンアップエラー: {e}")