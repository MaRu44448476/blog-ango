"""
Claude環境用記事生成モジュール
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

class ClaudeGenerator:
    """Claude環境用記事生成クラス"""
    
    def __init__(self, config):
        """
        Claude記事生成器を初期化
        
        Args:
            config: 設定オブジェクト
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 記事生成設定
        self.min_length = config.ARTICLE_MIN_LENGTH
        self.max_length = config.ARTICLE_MAX_LENGTH
        
    def generate_weekly_summary(self, news_data: List[Dict[str, Any]], 
                              market_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        週刊サマリー記事を生成（ClaudeCode環境用）
        
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
            
            # ClaudeCode環境では手動で記事を生成する必要があります
            # ここではテンプレート基盤の記事を生成
            article = self._generate_template_based_article(news_data, market_data)
            
            if article and self._validate_article_quality(article):
                # ソースニュースIDを追加
                article['source_news_ids'] = [news.get('id') for news in news_data[:7] if news.get('id')]
                return article
            else:
                self.logger.warning("生成された記事が品質基準を満たしません")
                
        except Exception as e:
            self.logger.error(f"週刊サマリー生成エラー: {e}")
        
        return None
    
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
    
    def _generate_template_based_article(self, news_data: List[Dict[str, Any]], 
                                       market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        テンプレートベースで記事を生成
        
        Args:
            news_data: ニュースデータ
            market_data: 市場データ
            
        Returns:
            Dict: 生成された記事データ
        """
        # 現在の週を取得
        now = datetime.now()
        week_start = now - timedelta(days=now.weekday())
        
        # トップニュースを選定
        top_news = sorted(news_data, key=lambda x: x.get('importance_score', 0), reverse=True)[:5]
        
        # 市場データから主要通貨の情報を抽出
        btc_data = next((item for item in market_data if item.get('symbol') == 'BTC'), {})
        eth_data = next((item for item in market_data if item.get('symbol') == 'ETH'), {})
        
        # 記事タイトル
        title = f"【週刊仮想通貨レポート】{week_start.month}月{week_start.day}日週の市場動向まとめ"
        
        # 記事本文を構成
        content = f"""
<h2>今週の仮想通貨市場概況</h2>
<p>今週の仮想通貨市場は、"""
        
        # 市場センチメントを分析
        if market_data:
            positive_coins = len([c for c in market_data if c.get('price_change_percentage_24h', 0) > 0])
            total_coins = len(market_data)
            if positive_coins / total_coins > 0.6:
                content += "全体的に上昇基調を維持し、投資家心理は改善傾向にありました。"
            elif positive_coins / total_coins < 0.4:
                content += "調整色が強く、慎重な姿勢が目立つ展開となりました。"
            else:
                content += "方向感に乏しく、レンジ相場が継続する状況でした。"
        else:
            content += "様々なニュースが市場を動かす一週間となりました。"
        
        content += "</p>\n\n"
        
        # 注目ニュースセクション
        content += "<h2>今週の注目ニュース</h2>\n\n"
        
        for i, news in enumerate(top_news, 1):
            content += f"<h3>{i}. {news.get('title', '')}</h3>\n"
            content += f"<p>{news.get('content', '')[:200]}{'...' if len(news.get('content', '')) > 200 else ''}</p>\n\n"
        
        # 市場分析セクション
        content += "<h2>市場分析</h2>\n"
        content += "<h3>主要通貨の週間パフォーマンス</h3>\n"
        content += "<ul>\n"
        
        if btc_data:
            btc_change = btc_data.get('price_change_percentage_24h', 0)
            btc_price = btc_data.get('price', 0)
            content += f"<li><strong>ビットコイン (BTC)</strong>: ${btc_price:,.0f} ({btc_change:+.1f}%)</li>\n"
        
        if eth_data:
            eth_change = eth_data.get('price_change_percentage_24h', 0)
            eth_price = eth_data.get('price', 0)
            content += f"<li><strong>イーサリアム (ETH)</strong>: ${eth_price:,.0f} ({eth_change:+.1f}%)</li>\n"
        
        content += "</ul>\n\n"
        
        # 来週の展望
        content += "<h2>来週の注目ポイント</h2>\n"
        content += "<p>来週は、"
        
        # 簡単な展望を追加
        if any('regulation' in news.get('title', '').lower() for news in top_news):
            content += "規制関連のニュースが続いており、政策動向に注目が集まりそうです。"
        elif any('bitcoin' in news.get('title', '').lower() for news in top_news):
            content += "ビットコインの動向が市場全体に影響を与える展開が予想されます。"
        else:
            content += "市場参加者の動向や新たなニュースの発表に注目が集まりそうです。"
        
        content += "</p>\n\n"
        
        # 免責事項
        content += "<p><strong>【重要な免責事項】</strong><br>"
        content += "本記事は情報提供を目的としており、投資助言ではありません。投資判断は自己責任でお願いします。</p>"
        
        # 文字数をカウント
        word_count = len(content.replace(' ', '').replace('\n', '').replace('<', '').replace('>', ''))
        
        article_data = {
            'title': title,
            'content': content,
            'word_count': word_count,
            'article_type': 'weekly_summary',
            'category': '週刊まとめ',
            'tags': ['仮想通貨', '週刊レポート', '市場分析', 'ビットコイン', 'イーサリアム'],
            'generation_date': datetime.now(),
            'metadata': {
                'generator': 'claude_template',
                'news_count': len(top_news),
                'market_data_count': len(market_data)
            }
        }
        
        self.logger.info(f"テンプレート記事生成完了: {word_count}字")
        return article_data
    
    def generate_news_article(self, news_item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        個別ニュース記事を生成
        
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
            
            article = self._generate_simple_news_article(news_item)
            
            if article and self._validate_article_quality(article):
                return article
            else:
                self.logger.warning("生成された記事が品質基準を満たしません")
                
        except Exception as e:
            self.logger.error(f"ニュース記事生成エラー: {e}")
        
        return None
    
    def _generate_simple_news_article(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        シンプルなニュース記事を生成
        
        Args:
            news_item: ニュースアイテム
            
        Returns:
            Dict: 記事データ
        """
        title = news_item.get('title', '')
        content = news_item.get('content', '')
        source = news_item.get('source', '')
        
        # 記事タイトル（速報タグを追加）
        if news_item.get('importance_score', 0) > 80:
            article_title = f"【速報】{title}"
        else:
            article_title = title
        
        # 記事本文を構成
        article_content = f"""
<h2>概要</h2>
<p>{content[:300]}{'...' if len(content) > 300 else ''}</p>

<h2>詳細</h2>
<p>{content}</p>

<h2>市場への影響</h2>
<p>この"""
        
        # 市場への影響を簡単に分析
        if 'bitcoin' in title.lower() or 'btc' in title.lower():
            article_content += "ビットコイン関連のニュースは、仮想通貨市場全体に大きな影響を与える可能性があります。"
        elif 'regulation' in title.lower() or '規制' in title.lower():
            article_content += "規制関連のニュースは、投資家心理や市場参加者の動向に影響を与える重要な要因となります。"
        else:
            article_content += "ニュースは、関連する仮想通貨や市場セグメントに影響を与える可能性があります。"
        
        article_content += "</p>\n\n"
        
        # まとめ
        article_content += "<h2>まとめ</h2>\n"
        article_content += f"<p>今回の{source.upper()}からの報道は、仮想通貨業界の動向を理解する上で重要な情報となります。引き続き関連する動向に注目していく必要があります。</p>\n\n"
        
        # ソース情報と免責事項
        article_content += f"<p><small>情報源: {source.upper()} | 投稿日: {datetime.now().strftime('%Y年%m月%d日')}</small></p>\n"
        article_content += "<p><strong>【重要な免責事項】</strong><br>本記事は情報提供を目的としており、投資助言ではありません。</p>"
        
        # カテゴリとタグを判定
        category = self._determine_article_category(news_item)
        tags = self._generate_tags(news_item, category)
        
        # 文字数をカウント
        word_count = len(article_content.replace(' ', '').replace('\n', '').replace('<', '').replace('>', ''))
        
        article_data = {
            'title': article_title,
            'content': article_content,
            'word_count': word_count,
            'article_type': 'news',
            'category': category,
            'tags': tags,
            'generation_date': datetime.now(),
            'source_news_ids': [news_item.get('id')] if news_item.get('id') else [],
            'original_source': news_item.get('source', ''),
            'original_url': news_item.get('url', ''),
            'importance_score': news_item.get('importance_score', 0),
            'metadata': {
                'generator': 'claude_simple',
                'original_content_length': len(content)
            }
        }
        
        self.logger.info(f"シンプル記事生成完了: {word_count}字")
        return article_data
    
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
        
        return True