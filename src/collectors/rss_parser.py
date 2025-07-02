"""
RSSフィードパーサーモジュール
"""

import feedparser
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import time
import re
from urllib.parse import urlparse
import hashlib

class RSSParser:
    """RSSフィードパーサークラス"""
    
    def __init__(self, config):
        """
        RSSパーサーを初期化
        
        Args:
            config: 設定オブジェクト
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # RSS フィード URL
        self.rss_feeds = config.RSS_FEEDS
        
        # キーワードリスト（日本語と英語）
        self.crypto_keywords = {
            "bitcoin": ["bitcoin", "btc", "ビットコイン"],
            "ethereum": ["ethereum", "eth", "イーサリアム", "イーサ"],
            "crypto": ["crypto", "cryptocurrency", "仮想通貨", "暗号資産", "デジタル通貨"],
            "blockchain": ["blockchain", "ブロックチェーン"],
            "defi": ["defi", "decentralized finance", "分散金融"],
            "nft": ["nft", "non-fungible token", "エヌエフティー"],
            "mining": ["mining", "マイニング", "採掘"],
            "trading": ["trading", "取引", "トレード"],
            "exchange": ["exchange", "取引所"],
            "wallet": ["wallet", "ウォレット"]
        }
        
        # ユーザーエージェント
        self.headers = {
            'User-Agent': 'CryptoMediaSystem/1.0 (+https://example.com/bot)'
        }
        
        # 除外キーワード
        self.exclude_keywords = [
            "advertisement", "sponsored", "ad:", "pr:",
            "広告", "スポンサー", "提供"
        ]
    
    def _calculate_importance_score(self, title: str, content: str, source: str) -> float:
        """
        記事の重要度スコアを計算
        
        Args:
            title: タイトル
            content: 内容
            source: ソース
            
        Returns:
            float: 重要度スコア (0-100)
        """
        score = 0.0
        text_lower = (title + " " + content).lower()
        
        # キーワードマッチング
        for category, keywords in self.crypto_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if category in ["bitcoin", "ethereum"]:
                        score += 10  # 主要通貨は高スコア
                    else:
                        score += 5
        
        # タイトルに重要キーワードがある場合はボーナス
        title_lower = title.lower()
        important_title_keywords = [
            "breaking", "urgent", "alert", "crash", "surge", "pump",
            "速報", "緊急", "急騰", "暴落", "高騰"
        ]
        
        for keyword in important_title_keywords:
            if keyword in title_lower:
                score += 15
        
        # ソースによる重み付け
        source_weights = {
            "coindesk": 1.2,
            "cointelegraph": 1.1,
            "decrypt": 1.0,
            "coinbureau": 0.9
        }
        
        source_weight = source_weights.get(source, 1.0)
        score *= source_weight
        
        # 除外キーワードがある場合はペナルティ
        for exclude_word in self.exclude_keywords:
            if exclude_word in text_lower:
                score *= 0.5
                break
        
        return min(score, 100.0)  # 最大100点
    
    def _extract_content_from_url(self, url: str) -> str:
        """
        URLから記事内容を抽出
        
        Args:
            url: 記事URL
            
        Returns:
            str: 抽出されたコンテンツ
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 一般的な記事コンテンツのタグを探す
                content_selectors = [
                    'article',
                    '.article-content',
                    '.post-content',
                    '.entry-content',
                    '.content',
                    'main'
                ]
                
                content = ""
                for selector in content_selectors:
                    elements = soup.select(selector)
                    if elements:
                        content = elements[0].get_text(strip=True)
                        break
                
                if not content:
                    # フォールバック: pタグから内容を抽出
                    paragraphs = soup.find_all('p')
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs[:5]])
                
                return content[:1000]  # 最初の1000文字まで
            
        except Exception as e:
            self.logger.warning(f"コンテンツ抽出エラー ({url}): {e}")
        
        return ""
    
    def _parse_feed(self, feed_url: str, source_name: str) -> List[Dict[str, Any]]:
        """
        単一のRSSフィードをパース
        
        Args:
            feed_url: フィードURL
            source_name: ソース名
            
        Returns:
            List[Dict]: パースされた記事リスト
        """
        try:
            self.logger.info(f"{source_name} フィードを解析中: {feed_url}")
            
            # フィードを取得
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                self.logger.warning(f"{source_name} フィード解析警告: {feed.bozo_exception}")
            
            articles = []
            
            for entry in feed.entries:
                try:
                    # 基本情報を抽出
                    title = entry.get('title', '').strip()
                    link = entry.get('link', '')
                    
                    if not title or not link:
                        continue
                    
                    # 公開日時を解析
                    publish_date = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        publish_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        publish_date = datetime(*entry.updated_parsed[:6])
                    
                    # 概要を取得
                    summary = entry.get('summary', '').strip()
                    if 'content' in entry:
                        content = entry.content[0].value if entry.content else summary
                    else:
                        content = summary
                    
                    # HTMLタグを除去
                    if content:
                        content = re.sub(r'<[^>]+>', '', content)
                        content = re.sub(r'\s+', ' ', content).strip()
                    
                    # 仮想通貨関連かチェック
                    if not self._is_crypto_related(title, content):
                        continue
                    
                    # 重要度スコアを計算
                    importance_score = self._calculate_importance_score(title, content, source_name)
                    
                    # 記事データを作成
                    article = {
                        'title': title,
                        'url': link,
                        'content': content,
                        'source': source_name,
                        'publish_date': publish_date,
                        'importance_score': importance_score,
                        'url_hash': hashlib.md5(link.encode()).hexdigest()
                    }
                    
                    articles.append(article)
                    
                except Exception as e:
                    self.logger.warning(f"記事処理エラー ({source_name}): {e}")
                    continue
            
            self.logger.info(f"{source_name} から {len(articles)} 件の記事を取得")
            return articles
            
        except Exception as e:
            self.logger.error(f"{source_name} フィード取得エラー: {e}")
            return []
    
    def _is_crypto_related(self, title: str, content: str) -> bool:
        """
        記事が仮想通貨関連かチェック
        
        Args:
            title: タイトル
            content: 内容
            
        Returns:
            bool: 仮想通貨関連かどうか
        """
        text = (title + " " + content).lower()
        
        # 仮想通貨関連キーワードをチェック
        for keywords in self.crypto_keywords.values():
            for keyword in keywords:
                if keyword in text:
                    return True
        
        return False
    
    def collect_latest_news(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        最新ニュースを収集
        
        Args:
            hours: 取得する時間範囲（時間）
            
        Returns:
            List[Dict]: ニュース記事リスト
        """
        all_articles = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        for source_name, feed_url in self.rss_feeds.items():
            try:
                articles = self._parse_feed(feed_url, source_name)
                
                # 指定時間内の記事のみフィルタ
                recent_articles = []
                for article in articles:
                    if article['publish_date'] and article['publish_date'] > cutoff_time:
                        recent_articles.append(article)
                    elif not article['publish_date']:
                        # 公開日時が不明な場合も含める
                        recent_articles.append(article)
                
                all_articles.extend(recent_articles)
                
                # レート制限のため少し待機
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"{source_name} 処理エラー: {e}")
                continue
        
        # 重要度スコアでソート
        all_articles.sort(key=lambda x: x['importance_score'], reverse=True)
        
        # 重複を除去（同じURLのものは除く）
        seen_urls = set()
        unique_articles = []
        
        for article in all_articles:
            if article['url_hash'] not in seen_urls:
                seen_urls.add(article['url_hash'])
                unique_articles.append(article)
        
        self.logger.info(f"合計 {len(unique_articles)} 件の最新ニュースを収集")
        return unique_articles
    
    def collect_weekly_news(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        週間ニュースを収集
        
        Args:
            days: 取得する日数
            
        Returns:
            List[Dict]: 週間ニュース記事リスト
        """
        return self.collect_latest_news(hours=days * 24)
    
    def get_top_stories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        トップストーリーを取得
        
        Args:
            limit: 取得する記事数
            
        Returns:
            List[Dict]: トップストーリーリスト
        """
        articles = self.collect_latest_news(hours=24)
        
        # 重要度スコアでソートして上位を返す
        top_articles = sorted(articles, key=lambda x: x['importance_score'], reverse=True)
        
        return top_articles[:limit]
    
    def categorize_news(self, articles: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        ニュースをカテゴリ別に分類
        
        Args:
            articles: 記事リスト
            
        Returns:
            Dict: カテゴリ別記事辞書
        """
        categorized = {
            "market": [],      # 市場・価格関連
            "technology": [],  # 技術関連
            "regulation": [],  # 規制関連
            "adoption": [],    # 採用・実用化関連
            "defi": [],       # DeFi関連
            "nft": [],        # NFT関連
            "general": []     # 一般
        }
        
        for article in articles:
            text = (article['title'] + " " + article['content']).lower()
            
            # カテゴリ分類キーワード
            if any(keyword in text for keyword in ["price", "trading", "market", "chart", "価格", "相場", "取引"]):
                categorized["market"].append(article)
            elif any(keyword in text for keyword in ["protocol", "upgrade", "fork", "consensus", "プロトコル", "アップグレード"]):
                categorized["technology"].append(article)
            elif any(keyword in text for keyword in ["regulation", "sec", "government", "legal", "規制", "法律", "政府"]):
                categorized["regulation"].append(article)
            elif any(keyword in text for keyword in ["adoption", "partnership", "integration", "採用", "導入", "提携"]):
                categorized["adoption"].append(article)
            elif any(keyword in text for keyword in ["defi", "yield", "liquidity", "staking", "分散金融"]):
                categorized["defi"].append(article)
            elif any(keyword in text for keyword in ["nft", "non-fungible", "collectible", "エヌエフティー"]):
                categorized["nft"].append(article)
            else:
                categorized["general"].append(article)
        
        return categorized
    
    def get_trending_topics(self, articles: List[Dict[str, Any]], limit: int = 5) -> List[str]:
        """
        トレンドトピックを抽出
        
        Args:
            articles: 記事リスト
            limit: 取得するトピック数
            
        Returns:
            List[str]: トレンドトピックリスト
        """
        # すべての記事のタイトルと内容を結合
        all_text = " ".join([article['title'] + " " + article['content'] for article in articles])
        
        # 単語頻度を計算（簡易版）
        words = re.findall(r'\b\w{3,}\b', all_text.lower())
        word_freq = {}
        
        for word in words:
            if word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # 頻度順にソート
        trending = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        return [word[0] for word in trending[:limit]]