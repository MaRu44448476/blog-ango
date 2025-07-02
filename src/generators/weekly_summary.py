"""
週刊ニュースまとめ記事生成モジュール
"""

import openai
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

class WeeklySummaryGenerator:
    """週刊サマリー生成クラス"""
    
    def __init__(self, config):
        """
        週刊サマリー生成器を初期化
        
        Args:
            config: 設定オブジェクト
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # OpenAI APIキーを設定
        openai.api_key = config.OPENAI_API_KEY
        
        # 記事生成設定
        self.min_length = config.ARTICLE_MIN_LENGTH
        self.max_length = config.ARTICLE_MAX_LENGTH
        
    def _create_weekly_prompt(self, news_data: List[Dict[str, Any]], 
                            market_data: List[Dict[str, Any]]) -> str:
        """
        週刊まとめ用のプロンプトを作成
        
        Args:
            news_data: ニュースデータ
            market_data: 市場データ
            
        Returns:
            str: 生成されたプロンプト
        """
        # トップニュースを選定（重要度スコア順）
        top_news = sorted(news_data, key=lambda x: x.get('importance_score', 0), reverse=True)[:7]
        
        # 市場データをまとめ
        market_summary = self._summarize_market_data(market_data)
        
        prompt = f"""
以下の情報を基に、今週の仮想通貨市場の動向をまとめた記事を日本語で作成してください。

【記事の構成要件】
1. 導入文（200字程度）- 今週の市場全体の概況
2. 重要ニュースの要約（各200-300字、5-7個のニュース）
3. 市場分析（300字程度）- 価格動向と市場心理
4. 来週の注目ポイント（200字程度）

【対象読者】
一般的な投資家向けにわかりやすく、専門用語は適度に解説を含めてください。

【今週の市場データ】
{market_summary}

【重要ニュース一覧】
"""
        
        for i, news in enumerate(top_news, 1):
            prompt += f"""
{i}. 【{news.get('source', '').upper()}】{news.get('title', '')}
   概要: {news.get('content', '')[:200]}...
   重要度: {news.get('importance_score', 0):.1f}/100
"""
        
        prompt += """

【記事作成指示】
- 記事全体で1500-2000字程度
- 見出しにはH2、H3タグを使用
- 重要な用語は**太字**で強調
- 投資助言は避け、情報提供に徹する
- 日本の読者に親しみやすい表現を使用
- WordPressに投稿するためのHTML形式で出力

記事タイトルも含めて出力してください。
        """
        
        return prompt
    
    def _summarize_market_data(self, market_data: List[Dict[str, Any]]) -> str:
        """
        市場データを要約
        
        Args:
            market_data: 市場データ
            
        Returns:
            str: 市場データの要約
        """
        if not market_data:
            return "市場データが取得できませんでした。"
        
        # 主要通貨のデータを抽出
        major_coins = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA']
        major_data = [coin for coin in market_data if coin.get('symbol') in major_coins]
        
        summary = "【主要通貨の週間パフォーマンス】\n"
        
        for coin in major_data[:5]:  # 上位5通貨
            symbol = coin.get('symbol', '')
            price = coin.get('price', 0)
            change_24h = coin.get('price_change_percentage_24h', 0)
            change_7d = coin.get('price_change_percentage_7d', 0)
            
            summary += f"- {symbol}: ${price:,.2f} (24h: {change_24h:+.1f}%"
            if change_7d:
                summary += f", 7d: {change_7d:+.1f}%"
            summary += ")\n"
        
        # 市場全体の動向
        if market_data:
            positive_coins = len([c for c in market_data if c.get('price_change_percentage_24h', 0) > 0])
            total_coins = len(market_data)
            positive_ratio = positive_coins / total_coins * 100 if total_coins > 0 else 0
            
            summary += f"\n市場センチメント: 全{total_coins}通貨中{positive_coins}通貨が上昇（{positive_ratio:.1f}%）"
        
        return summary
    
    def _generate_article_with_openai(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        OpenAI APIを使用して記事を生成
        
        Args:
            prompt: 生成プロンプト
            
        Returns:
            Dict: 生成された記事データ
        """
        try:
            self.logger.info("OpenAI APIで記事生成を開始")
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは仮想通貨専門のジャーナリストです。正確で分かりやすい記事を作成してください。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=3000,
                temperature=0.7,
                top_p=0.9
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
                    'article_type': 'weekly_summary',
                    'category': '週刊まとめ',
                    'tags': ['仮想通貨', '週刊レポート', '市場分析', 'ビットコイン', 'イーサリアム'],
                    'generation_date': datetime.now(),
                    'metadata': {
                        'model_used': 'gpt-4',
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }
                }
                
                self.logger.info(f"記事生成成功: {word_count}字")
                return article_data
            
        except Exception as e:
            self.logger.error(f"OpenAI API記事生成エラー: {e}")
        
        return None
    
    def generate_summary(self, news_data: List[Dict[str, Any]], 
                        market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        週刊サマリー記事を生成
        
        Args:
            news_data: ニュースデータ
            market_data: 市場データ
            
        Returns:
            Dict: 生成された記事
        """
        try:
            if not news_data:
                self.logger.warning("ニュースデータが空です")
                return None
            
            # プロンプトを作成
            prompt = self._create_weekly_prompt(news_data, market_data)
            
            # OpenAI APIで記事生成
            article = self._generate_article_with_openai(prompt)
            
            if article:
                # 記事の品質をチェック
                if self._validate_article_quality(article):
                    # ソースニュースIDを追加
                    article['source_news_ids'] = [news.get('id') for news in news_data[:7] if news.get('id')]
                    return article
                else:
                    self.logger.warning("生成された記事が品質基準を満たしません")
            
        except Exception as e:
            self.logger.error(f"週刊サマリー生成エラー: {e}")
        
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
        
        # 基本的なHTML構造チェック
        content = article.get('content', '')
        if '<h2>' not in content and '<h3>' not in content:
            self.logger.warning("記事に適切な見出し構造がありません")
            return False
        
        return True
    
    def create_weekly_template(self) -> str:
        """
        週刊記事のテンプレートを作成
        
        Returns:
            str: テンプレート文字列
        """
        template = """
<h2>今週の仮想通貨市場概況</h2>
<p>今週の仮想通貨市場は...</p>

<h2>注目ニュース</h2>

<h3>1. ビットコイン関連</h3>
<p>ビットコインに関する重要なニュース...</p>

<h3>2. イーサリアム関連</h3>
<p>イーサリアムに関する重要なニュース...</p>

<h3>3. 規制・政策関連</h3>
<p>規制や政策に関するニュース...</p>

<h3>4. DeFi・NFT関連</h3>
<p>DeFiやNFTに関するニュース...</p>

<h3>5. その他の注目ニュース</h3>
<p>その他の重要なニュース...</p>

<h2>市場分析</h2>
<p>今週の価格動向と市場心理について...</p>

<h2>来週の注目ポイント</h2>
<p>来週注目すべきポイント...</p>

<hr>
<p><small>※本記事は情報提供を目的としており、投資助言ではありません。投資判断は自己責任でお願いします。</small></p>
        """
        
        return template.strip()
    
    def generate_seo_optimized_title(self, news_data: List[Dict[str, Any]]) -> str:
        """
        SEO最適化されたタイトルを生成
        
        Args:
            news_data: ニュースデータ
            
        Returns:
            str: SEO最適化タイトル
        """
        # 現在の週を取得
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        month = week_start.month
        day = week_start.day
        
        # 主要キーワードを抽出
        keywords = []
        for news in news_data[:3]:
            title = news.get('title', '').lower()
            if 'bitcoin' in title or 'btc' in title or 'ビットコイン' in title:
                keywords.append('ビットコイン')
            elif 'ethereum' in title or 'eth' in title or 'イーサリアム' in title:
                keywords.append('イーサリアム')
            elif 'regulation' in title or '規制' in title:
                keywords.append('規制')
        
        # タイトルパターンを選択
        title_patterns = [
            f"【仮想通貨週報】{month}月{day}日週の重要ニュースまとめ",
            f"今週の仮想通貨市場動向｜{month}/{day}週間レポート",
            f"暗号資産週刊ニュース｜{month}月第{(day-1)//7+1}週の注目トピック"
        ]
        
        if keywords:
            keyword_str = '・'.join(keywords[:2])
            title_patterns.append(f"【{keyword_str}】仮想通貨週間ニュースまとめ｜{month}月{day}日週")
        
        return title_patterns[0]  # デフォルトで最初のパターンを使用