"""
ニュース記事生成モジュール
"""

import openai
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

class NewsWriter:
    """ニュース記事生成クラス"""
    
    def __init__(self, config):
        """
        ニュース記事生成器を初期化
        
        Args:
            config: 設定オブジェクト
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # OpenAI APIキーを設定
        openai.api_key = config.OPENAI_API_KEY
        
        # 記事生成設定
        self.min_length = 500  # 速報記事は短め
        self.max_length = 800
        
    def _create_news_prompt(self, news_item: Dict[str, Any]) -> str:
        """
        ニュース記事用のプロンプトを作成
        
        Args:
            news_item: ニュースアイテム
            
        Returns:
            str: 生成されたプロンプト
        """
        title = news_item.get('title', '')
        content = news_item.get('content', '')
        source = news_item.get('source', '')
        
        prompt = f"""
以下のニュース情報を基に、日本語で仮想通貨ニュース記事を作成してください。

【元ニュース情報】
タイトル: {title}
ソース: {source.upper()}
内容: {content}

【記事作成要件】
1. 文字数: 500-800字程度
2. 構成: 見出し、リード文、本文、まとめ
3. 対象読者: 仮想通貨に関心のある一般投資家
4. 語調: 客観的で分かりやすい日本語
5. 専門用語には適度な解説を含める
6. 投資助言は避け、情報提供に徹する

【記事構成】
- H2タグを使った適切な見出し構造
- 重要なポイントは**太字**で強調
- WordPressに投稿するためのHTML形式
- 最後に情報源を明記

【注意事項】
- 元ニュースの内容を正確に伝える
- 誇張や憶測は避ける
- 日本の読者に理解しやすい表現を使用
- SEOを意識したタイトル作成

記事タイトルと本文を出力してください。
        """
        
        return prompt
    
    def _determine_article_category(self, news_item: Dict[str, Any]) -> str:
        """
        記事のカテゴリを判定
        
        Args:
            news_item: ニュースアイテム
            
        Returns:
            str: カテゴリ名
        """
        text = (news_item.get('title', '') + ' ' + news_item.get('content', '')).lower()
        
        # カテゴリ判定ロジック
        if any(keyword in text for keyword in ['price', 'trading', 'market', 'chart', '価格', '相場', '取引']):
            return '市場・価格'
        elif any(keyword in text for keyword in ['regulation', 'sec', 'government', 'legal', '規制', '法律']):
            return '規制・政策'
        elif any(keyword in text for keyword in ['bitcoin', 'btc', 'ビットコイン']):
            return 'ビットコイン'
        elif any(keyword in text for keyword in ['ethereum', 'eth', 'イーサリアム']):
            return 'イーサリアム'
        elif any(keyword in text for keyword in ['defi', 'yield', 'liquidity', '分散金融']):
            return 'DeFi'
        elif any(keyword in text for keyword in ['nft', 'non-fungible', 'エヌエフティー']):
            return 'NFT'
        elif any(keyword in text for keyword in ['adoption', 'partnership', '採用', '提携']):
            return '普及・採用'
        else:
            return '仮想通貨ニュース'
    
    def _generate_tags(self, news_item: Dict[str, Any], category: str) -> List[str]:
        """
        記事のタグを生成
        
        Args:
            news_item: ニュースアイテム
            category: カテゴリ
            
        Returns:
            List[str]: タグリスト
        """
        text = (news_item.get('title', '') + ' ' + news_item.get('content', '')).lower()
        tags = ['仮想通貨', '暗号資産']
        
        # 基本タグ
        if 'bitcoin' in text or 'btc' in text or 'ビットコイン' in text:
            tags.append('ビットコイン')
        if 'ethereum' in text or 'eth' in text or 'イーサリアム' in text:
            tags.append('イーサリアム')
        if 'binance' in text or 'bnb' in text:
            tags.append('バイナンス')
        if 'defi' in text or '分散金融' in text:
            tags.append('DeFi')
        if 'nft' in text:
            tags.append('NFT')
        if 'regulation' in text or '規制' in text:
            tags.append('規制')
        if 'trading' in text or '取引' in text:
            tags.append('取引')
        if 'mining' in text or 'マイニング' in text:
            tags.append('マイニング')
        
        # カテゴリベースのタグ
        if category not in tags:
            tags.append(category)
        
        return list(set(tags))  # 重複を除去
    
    def generate_news_article(self, news_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        ニュース記事を生成
        
        Args:
            news_item: ニュースアイテム
            
        Returns:
            Dict: 生成された記事データ
        """
        try:
            if not news_item.get('title') or not news_item.get('content'):
                self.logger.warning("ニュースアイテムに必要な情報が不足しています")
                return None
            
            # 重要度スコアが低い記事はスキップ
            if news_item.get('importance_score', 0) < 30:
                self.logger.info(f"重要度が低いため記事生成をスキップ: {news_item.get('importance_score')}")
                return None
            
            # プロンプトを作成
            prompt = self._create_news_prompt(news_item)
            
            # OpenAI APIで記事生成
            article = self._generate_article_with_openai(prompt)
            
            if article:
                # カテゴリとタグを設定
                category = self._determine_article_category(news_item)
                tags = self._generate_tags(news_item, category)
                
                article.update({
                    'article_type': 'news',
                    'category': category,
                    'tags': tags,
                    'source_news_ids': [news_item.get('id')] if news_item.get('id') else [],
                    'original_source': news_item.get('source', ''),
                    'original_url': news_item.get('url', ''),
                    'importance_score': news_item.get('importance_score', 0)
                })
                
                # 記事の品質をチェック
                if self._validate_article_quality(article):
                    return article
                else:
                    self.logger.warning("生成された記事が品質基準を満たしません")
            
        except Exception as e:
            self.logger.error(f"ニュース記事生成エラー: {e}")
        
        return None
    
    def _generate_article_with_openai(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        OpenAI APIを使用して記事を生成
        
        Args:
            prompt: 生成プロンプト
            
        Returns:
            Dict: 生成された記事データ
        """
        try:
            self.logger.info("OpenAI APIでニュース記事生成を開始")
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは仮想通貨専門のニュースライターです。正確で分かりやすい記事を迅速に作成してください。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.6,
                top_p=0.8
            )
            
            if response.choices:
                content = response.choices[0].message.content.strip()
                
                # タイトルと本文を分離
                lines = content.split('\n')
                title = lines[0].replace('#', '').strip()
                body = '\n'.join(lines[1:]).strip()
                
                # 文字数をカウント
                word_count = len(body.replace(' ', '').replace('\n', ''))
                
                article_data = {
                    'title': title,
                    'content': body,
                    'word_count': word_count,
                    'generation_date': datetime.now(),
                    'metadata': {
                        'model_used': 'gpt-4',
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }
                }
                
                self.logger.info(f"ニュース記事生成成功: {word_count}字")
                return article_data
            
        except Exception as e:
            self.logger.error(f"OpenAI APIニュース記事生成エラー: {e}")
        
        return None
    
    def _validate_article_quality(self, article: Dict[str, Any]) -> bool:
        """
        記事の品質を検証
        
        Args:
            article: 記事データ
            
        Returns:
            bool: 品質基準を満たすかどうか
        """
        # 最小文字数チェック
        if article.get('word_count', 0) < self.min_length:
            self.logger.warning(f"記事が短すぎます: {article.get('word_count')}文字")
            return False
        
        # 最大文字数チェック
        if article.get('word_count', 0) > self.max_length:
            self.logger.warning(f"記事が長すぎます: {article.get('word_count')}文字")
            return False
        
        # タイトルの存在チェック
        if not article.get('title'):
            self.logger.warning("タイトルが存在しません")
            return False
        
        # 内容の存在チェック
        if not article.get('content'):
            self.logger.warning("記事内容が存在しません")
            return False
        
        # 重複チェック（簡易版）
        content = article.get('content', '')
        sentences = re.split(r'[。！？]', content)
        unique_sentences = set(sentence.strip() for sentence in sentences if sentence.strip())
        
        if len(unique_sentences) < len(sentences) * 0.8:  # 80%以上がユニークでない場合
            self.logger.warning("記事に重複した内容が多すぎます")
            return False
        
        return True
    
    def generate_breaking_news(self, news_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        速報記事を生成
        
        Args:
            news_item: ニュースアイテム
            
        Returns:
            Dict: 生成された速報記事
        """
        try:
            # 速報記事用の短いプロンプト
            prompt = f"""
以下のニュースを基に、簡潔な速報記事を日本語で作成してください。

【元ニュース】
{news_item.get('title', '')}
{news_item.get('content', '')[:300]}

【要件】
- 300-500字程度の簡潔な記事
- 重要なポイントを明確に伝える
- 速報らしい緊急感のある文体
- HTML形式で出力
- タイトルに【速報】を含める

タイトルと本文を出力してください。
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # 速報なので高速なモデルを使用
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは仮想通貨の速報記事を作成する専門ライターです。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.5
            )
            
            if response.choices:
                content = response.choices[0].message.content.strip()
                lines = content.split('\n')
                title = lines[0].replace('#', '').strip()
                body = '\n'.join(lines[1:]).strip()
                
                word_count = len(body.replace(' ', '').replace('\n', ''))
                
                article_data = {
                    'title': title,
                    'content': body,
                    'word_count': word_count,
                    'article_type': 'breaking_news',
                    'category': '速報',
                    'tags': ['速報', '仮想通貨'] + self._generate_tags(news_item, '速報'),
                    'generation_date': datetime.now(),
                    'source_news_ids': [news_item.get('id')] if news_item.get('id') else [],
                    'priority': 'high',
                    'metadata': {
                        'model_used': 'gpt-3.5-turbo',
                        'is_breaking_news': True
                    }
                }
                
                self.logger.info(f"速報記事生成成功: {word_count}字")
                return article_data
            
        except Exception as e:
            self.logger.error(f"速報記事生成エラー: {e}")
        
        return None
    
    def batch_generate_news(self, news_items: List[Dict[str, Any]], 
                           max_articles: int = 5) -> List[Dict[str, Any]]:
        """
        複数のニュース記事を一括生成
        
        Args:
            news_items: ニュースアイテムのリスト
            max_articles: 最大記事数
            
        Returns:
            List[Dict]: 生成された記事のリスト
        """
        generated_articles = []
        
        # 重要度順にソート
        sorted_news = sorted(news_items, key=lambda x: x.get('importance_score', 0), reverse=True)
        
        for i, news_item in enumerate(sorted_news[:max_articles]):
            try:
                self.logger.info(f"記事生成中 ({i+1}/{min(len(sorted_news), max_articles)})")
                
                # 重要度が非常に高い場合は速報記事として生成
                if news_item.get('importance_score', 0) > 80:
                    article = self.generate_breaking_news(news_item)
                else:
                    article = self.generate_news_article(news_item)
                
                if article:
                    generated_articles.append(article)
                    
                # API制限を避けるため少し待機
                import time
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"記事生成エラー ({i+1}): {e}")
                continue
        
        self.logger.info(f"一括記事生成完了: {len(generated_articles)}件")
        return generated_articles