"""
WordPress投稿クライアントモジュール
"""

import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import base64
import json
from urllib.parse import urljoin

class WordPressClient:
    """WordPress REST API クライアント"""
    
    def __init__(self, config):
        """
        WordPress クライアントを初期化
        
        Args:
            config: 設定オブジェクト
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # WordPress設定
        self.wp_url = config.WP_URL.rstrip('/')
        self.wp_username = config.WP_USERNAME
        self.wp_password = config.WP_PASSWORD
        
        # REST API エンドポイント
        self.api_base = f"{self.wp_url}/wp-json/wp/v2"
        
        # 認証ヘッダー
        credentials = f"{self.wp_username}:{self.wp_password}"
        token = base64.b64encode(credentials.encode()).decode()
        
        self.headers = {
            'Authorization': f'Basic {token}',
            'Content-Type': 'application/json',
            'User-Agent': 'CryptoMediaSystem/1.0'
        }
        
        # カテゴリとタグのキャッシュ
        self._categories_cache = {}
        self._tags_cache = {}
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """
        WordPress REST APIへのリクエストを実行
        
        Args:
            method: HTTPメソッド
            endpoint: エンドポイント
            data: リクエストデータ
            
        Returns:
            Dict: レスポンスデータ
        """
        url = urljoin(self.api_base + '/', endpoint)
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=30)
            else:
                self.logger.error(f"サポートされていないHTTPメソッド: {method}")
                return None
            
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 401:
                self.logger.error("WordPress認証エラー: ユーザー名/パスワードを確認してください")
            elif response.status_code == 403:
                self.logger.error("WordPress権限エラー: 投稿権限がありません")
            elif response.status_code == 404:
                self.logger.error(f"WordPress APIエンドポイントが見つかりません: {url}")
            else:
                self.logger.error(f"WordPress API エラー: {response.status_code} - {response.text}")
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"WordPress API リクエストエラー: {e}")
        
        return None
    
    def test_connection(self) -> bool:
        """
        WordPress接続をテスト
        
        Returns:
            bool: 接続が成功したかどうか
        """
        try:
            # サイト情報を取得してテスト
            site_info = self._make_request('GET', '')
            if site_info:
                self.logger.info(f"WordPress接続成功: {site_info.get('name', 'Unknown Site')}")
                return True
            else:
                self.logger.error("WordPress接続テスト失敗")
                return False
                
        except Exception as e:
            self.logger.error(f"WordPress接続テストエラー: {e}")
            return False
    
    def get_or_create_category(self, category_name: str) -> Optional[int]:
        """
        カテゴリを取得または作成
        
        Args:
            category_name: カテゴリ名
            
        Returns:
            int: カテゴリID
        """
        # キャッシュをチェック
        if category_name in self._categories_cache:
            return self._categories_cache[category_name]
        
        try:
            # 既存カテゴリを検索
            categories = self._make_request('GET', f'categories?search={category_name}')
            
            if categories:
                for category in categories:
                    if category['name'] == category_name:
                        self._categories_cache[category_name] = category['id']
                        return category['id']
            
            # カテゴリが存在しない場合は作成
            new_category_data = {
                'name': category_name,
                'slug': category_name.lower().replace(' ', '-').replace('・', '-')
            }
            
            new_category = self._make_request('POST', 'categories', new_category_data)
            
            if new_category:
                category_id = new_category['id']
                self._categories_cache[category_name] = category_id
                self.logger.info(f"新しいカテゴリを作成: {category_name} (ID: {category_id})")
                return category_id
            
        except Exception as e:
            self.logger.error(f"カテゴリ取得/作成エラー: {e}")
        
        return None
    
    def get_or_create_tags(self, tag_names: List[str]) -> List[int]:
        """
        タグを取得または作成
        
        Args:
            tag_names: タグ名のリスト
            
        Returns:
            List[int]: タグIDのリスト
        """
        tag_ids = []
        
        for tag_name in tag_names:
            # キャッシュをチェック
            if tag_name in self._tags_cache:
                tag_ids.append(self._tags_cache[tag_name])
                continue
            
            try:
                # 既存タグを検索
                tags = self._make_request('GET', f'tags?search={tag_name}')
                
                tag_found = False
                if tags:
                    for tag in tags:
                        if tag['name'] == tag_name:
                            self._tags_cache[tag_name] = tag['id']
                            tag_ids.append(tag['id'])
                            tag_found = True
                            break
                
                # タグが存在しない場合は作成
                if not tag_found:
                    new_tag_data = {
                        'name': tag_name,
                        'slug': tag_name.lower().replace(' ', '-').replace('・', '-')
                    }
                    
                    new_tag = self._make_request('POST', 'tags', new_tag_data)
                    
                    if new_tag:
                        tag_id = new_tag['id']
                        self._tags_cache[tag_name] = tag_id
                        tag_ids.append(tag_id)
                        self.logger.info(f"新しいタグを作成: {tag_name} (ID: {tag_id})")
                
            except Exception as e:
                self.logger.error(f"タグ取得/作成エラー ({tag_name}): {e}")
                continue
        
        return tag_ids
    
    def create_featured_image(self, title: str) -> Optional[int]:
        """
        アイキャッチ画像を作成（プレースホルダー）
        
        Args:
            title: 記事タイトル
            
        Returns:
            int: メディアID
        """
        # 注意: 実際の実装では画像生成APIや既存の画像を使用
        # ここでは簡易的な実装例
        try:
            # 既存のプレースホルダー画像を検索
            media = self._make_request('GET', 'media?search=crypto-placeholder')
            
            if media and len(media) > 0:
                return media[0]['id']
            
            self.logger.info("アイキャッチ画像が見つかりません（プレースホルダー画像を用意してください）")
            
        except Exception as e:
            self.logger.error(f"アイキャッチ画像作成エラー: {e}")
        
        return None
    
    def publish_article(self, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        記事をWordPressに投稿
        
        Args:
            article: 記事データ
            
        Returns:
            Dict: 投稿結果
        """
        try:
            self.logger.info(f"WordPressに記事を投稿中: {article.get('title', 'No Title')}")
            
            # カテゴリIDを取得
            category_id = None
            if article.get('category'):
                category_id = self.get_or_create_category(article['category'])
            
            # タグIDを取得
            tag_ids = []
            if article.get('tags'):
                tag_ids = self.get_or_create_tags(article['tags'])
            
            # アイキャッチ画像を設定（オプション）
            featured_media_id = self.create_featured_image(article.get('title', ''))
            
            # 投稿データを準備
            post_data = {
                'title': article.get('title', ''),
                'content': article.get('content', ''),
                'status': 'publish',  # 即座に公開
                'author': 1,  # デフォルトの作成者ID
                'excerpt': self._create_excerpt(article.get('content', '')),
                'date': datetime.now().isoformat(),
                'categories': [category_id] if category_id else [],
                'tags': tag_ids,
                'meta': {
                    'crypto_article_type': article.get('article_type', ''),
                    'crypto_importance_score': article.get('importance_score', 0),
                    'crypto_word_count': article.get('word_count', 0),
                    'crypto_generation_date': article.get('generation_date', datetime.now()).isoformat() if article.get('generation_date') else None
                }
            }
            
            # アイキャッチ画像を設定
            if featured_media_id:
                post_data['featured_media'] = featured_media_id
            
            # 記事を投稿
            result = self._make_request('POST', 'posts', post_data)
            
            if result:
                post_id = result['id']
                post_url = result['link']
                
                self.logger.info(f"記事投稿成功: ID {post_id} - {post_url}")
                
                return {
                    'id': post_id,
                    'url': post_url,
                    'status': result['status'],
                    'date': result['date'],
                    'title': result['title']['rendered'],
                    'success': True
                }
            else:
                self.logger.error("記事投稿失敗")
                return {
                    'success': False,
                    'error_message': 'WordPress API request failed'
                }
                
        except Exception as e:
            self.logger.error(f"記事投稿エラー: {e}")
            return {
                'success': False,
                'error_message': str(e)
            }
    
    def _create_excerpt(self, content: str, length: int = 160) -> str:
        """
        記事の抜粋を作成
        
        Args:
            content: 記事内容
            length: 抜粋の長さ
            
        Returns:
            str: 抜粋
        """
        # HTMLタグを除去
        import re
        clean_content = re.sub(r'<[^>]+>', '', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        if len(clean_content) <= length:
            return clean_content
        
        # 指定の長さで切り詰め、最後の完全な単語で終わるようにする
        excerpt = clean_content[:length]
        last_space = excerpt.rfind(' ')
        
        if last_space > length * 0.8:  # 80%以上の位置に空白がある場合
            excerpt = excerpt[:last_space]
        
        return excerpt + '...'
    
    def update_article(self, post_id: int, article: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        記事を更新
        
        Args:
            post_id: 投稿ID
            article: 更新する記事データ
            
        Returns:
            Dict: 更新結果
        """
        try:
            self.logger.info(f"記事を更新中: ID {post_id}")
            
            update_data = {
                'title': article.get('title', ''),
                'content': article.get('content', ''),
                'excerpt': self._create_excerpt(article.get('content', ''))
            }
            
            result = self._make_request('PUT', f'posts/{post_id}', update_data)
            
            if result:
                self.logger.info(f"記事更新成功: ID {post_id}")
                return {
                    'id': result['id'],
                    'url': result['link'],
                    'success': True
                }
            else:
                return {
                    'success': False,
                    'error_message': 'Update failed'
                }
                
        except Exception as e:
            self.logger.error(f"記事更新エラー: {e}")
            return {
                'success': False,
                'error_message': str(e)
            }
    
    def delete_article(self, post_id: int) -> bool:
        """
        記事を削除
        
        Args:
            post_id: 投稿ID
            
        Returns:
            bool: 削除が成功したかどうか
        """
        try:
            self.logger.info(f"記事を削除中: ID {post_id}")
            
            result = self._make_request('DELETE', f'posts/{post_id}')
            
            if result:
                self.logger.info(f"記事削除成功: ID {post_id}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"記事削除エラー: {e}")
            return False
    
    def batch_publish_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        複数の記事を一括投稿
        
        Args:
            articles: 記事データのリスト
            
        Returns:
            List[Dict]: 投稿結果のリスト
        """
        results = []
        
        for i, article in enumerate(articles):
            try:
                self.logger.info(f"一括投稿中 ({i+1}/{len(articles)})")
                
                result = self.publish_article(article)
                results.append(result)
                
                # レート制限を避けるため少し待機
                import time
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"一括投稿エラー ({i+1}): {e}")
                results.append({
                    'success': False,
                    'error_message': str(e)
                })
                continue
        
        successful_posts = len([r for r in results if r.get('success')])
        self.logger.info(f"一括投稿完了: {successful_posts}/{len(articles)} 件成功")
        
        return results
    
    def get_recent_posts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        最近の投稿を取得
        
        Args:
            limit: 取得する投稿数
            
        Returns:
            List[Dict]: 投稿リスト
        """
        try:
            posts = self._make_request('GET', f'posts?per_page={limit}&orderby=date&order=desc')
            
            if posts:
                return posts
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"最近の投稿取得エラー: {e}")
            return []