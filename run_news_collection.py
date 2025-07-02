#!/usr/bin/env python3
"""
仮想通貨ニュース収集実行スクリプト
"""

import sys
import json
from datetime import datetime

# 最小限のRSSパーサー（依存関係なし）
try:
    import urllib.request
    import xml.etree.ElementTree as ET
    from urllib.parse import urljoin
except ImportError as e:
    print(f"❌ 必要なモジュールが不足: {e}")
    sys.exit(1)

def parse_rss_feed(feed_url, source_name):
    """RSSフィードを解析"""
    print(f"📡 {source_name} からニュースを取得中...")
    
    try:
        headers = {
            'User-Agent': 'CryptoMediaSystem/1.0 (+https://crypto-dictionary.net)'
        }
        
        request = urllib.request.Request(feed_url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read().decode('utf-8')
            
        # XMLをパース
        root = ET.fromstring(content)
        
        # RSS 2.0 形式を想定
        items = []
        
        # channelまたはrssの下のitemを探す
        for item in root.findall('.//item'):
            title_elem = item.find('title')
            link_elem = item.find('link')
            description_elem = item.find('description')
            pubdate_elem = item.find('pubDate')
            
            if title_elem is not None and link_elem is not None:
                title = title_elem.text or ""
                link = link_elem.text or ""
                description = description_elem.text or "" if description_elem is not None else ""
                pubdate = pubdate_elem.text or "" if pubdate_elem is not None else ""
                
                # 仮想通貨関連かチェック
                if is_crypto_related(title, description):
                    items.append({
                        'title': title.strip(),
                        'url': link.strip(),
                        'description': description.strip()[:300],
                        'source': source_name,
                        'pubdate': pubdate,
                        'importance_score': calculate_importance(title, description)
                    })
        
        print(f"✅ {source_name}: {len(items)}件の仮想通貨関連ニュースを取得")
        return items
        
    except Exception as e:
        print(f"❌ {source_name} エラー: {e}")
        return []

def is_crypto_related(title, description):
    """仮想通貨関連ニュースかチェック"""
    text = (title + " " + description).lower()
    
    crypto_keywords = [
        'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
        'blockchain', 'defi', 'nft', 'altcoin', 'trading', 'exchange',
        'ビットコイン', '仮想通貨', '暗号資産', 'イーサリアム', 'ブロックチェーン'
    ]
    
    return any(keyword in text for keyword in crypto_keywords)

def calculate_importance(title, description):
    """重要度スコアを計算（改良版）"""
    text = (title + " " + description).lower()
    score = 0
    
    # 基本スコア（仮想通貨関連なら最低30点）
    score = 30
    
    # 超重要キーワード（高スコア）
    high_impact_keywords = {
        'breaking': 25, 'urgent': 25, 'alert': 20,
        'crash': 20, 'surge': 18, 'soar': 18, 'plunge': 20,
        'record': 15, 'ath': 15, 'all-time high': 15,
        'sec approves': 20, 'sec approval': 20, 'etf': 18,
        'regulation': 15, 'government': 12, 'ban': 18,
        'hack': 15, 'hacked': 15, 'exploit': 12,
        'partnership': 12, 'acquisition': 15, 'merger': 15
    }
    
    # 人気通貨（日本で注目度高い）
    popular_coins = {
        'bitcoin': 15, 'btc': 15, 'ethereum': 12, 'eth': 12,
        'xrp': 10, 'ripple': 10, 'ada': 8, 'cardano': 8,
        'sol': 10, 'solana': 10, 'doge': 8, 'dogecoin': 8
    }
    
    # 価格関連（日本人投資家が最も関心を持つ）
    price_keywords = {
        'price': 12, '$': 8, 'hits': 10, 'reaches': 8,
        'rally': 10, 'pump': 10, 'dump': 12, 'correction': 8,
        'bull': 8, 'bear': 8, 'market': 6
    }
    
    # 機関投資・企業関連
    institutional_keywords = {
        'institutional': 12, 'fund': 10, 'investment': 8,
        'corporate': 10, 'treasury': 12, 'adoption': 10,
        'microstrategy': 15, 'tesla': 15, 'blackrock': 18
    }
    
    # DeFi・技術関連
    tech_keywords = {
        'defi': 8, 'yield': 6, 'staking': 8, 'protocol': 6,
        'upgrade': 8, 'fork': 8, 'consensus': 6, 'layer': 6
    }
    
    # 各カテゴリーでスコア加算
    for keyword, points in high_impact_keywords.items():
        if keyword in text:
            score += points
    
    for keyword, points in popular_coins.items():
        if keyword in text:
            score += points
    
    for keyword, points in price_keywords.items():
        if keyword in text:
            score += points
    
    for keyword, points in institutional_keywords.items():
        if keyword in text:
            score += points
    
    for keyword, points in tech_keywords.items():
        if keyword in text:
            score += points
    
    # 複数の重要要素が含まれている場合はボーナス
    important_count = sum(1 for category in [high_impact_keywords, popular_coins, price_keywords, institutional_keywords] 
                         for keyword in category if keyword in text)
    if important_count >= 3:
        score += 10  # 複数要素ボーナス
    
    # タイトルに重要キーワードがある場合はボーナス
    title_lower = title.lower()
    if any(keyword in title_lower for keyword in ['bitcoin', 'btc', 'ethereum', 'eth', 'breaking', 'surge', 'crash']):
        score += 5
    
    return min(score, 100)

def collect_crypto_news():
    """仮想通貨ニュースを収集"""
    
    # 主要なRSSフィード（高品質ニュースソース）
    rss_feeds = {
        'CoinDesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'CoinTelegraph': 'https://cointelegraph.com/rss',
        'Decrypt': 'https://decrypt.co/feed',
        'TheBlock': 'https://www.theblock.co/rss.xml',
        'CryptoSlate': 'https://cryptoslate.com/feed/',
        'U.Today': 'https://u.today/rss',
        'BeInCrypto': 'https://beincrypto.com/feed/'
    }
    
    all_news = []
    
    print("🚀 仮想通貨ニュース収集開始")
    print("=" * 50)
    
    for source_name, feed_url in rss_feeds.items():
        news_items = parse_rss_feed(feed_url, source_name)
        all_news.extend(news_items)
    
    # 重要度順でソート
    all_news.sort(key=lambda x: x['importance_score'], reverse=True)
    
    print("\n" + "=" * 50)
    print(f"📊 合計 {len(all_news)} 件のニュースを収集")
    
    # トップ10を表示
    print("\n🔥 重要度上位ニュース:")
    for i, news in enumerate(all_news[:10], 1):
        print(f"{i:2d}. [{news['source']}] {news['title'][:60]}{'...' if len(news['title']) > 60 else ''}")
        print(f"    重要度: {news['importance_score']:.1f}/100")
        print(f"    URL: {news['url']}")
        print()
    
    return all_news

def save_news_data(news_items):
    """ニュースデータをJSONファイルに保存"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"collected_news_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_count': len(news_items),
                'news_items': news_items
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 ニュースデータを保存: {filename}")
        return filename
    except Exception as e:
        print(f"❌ ファイル保存エラー: {e}")
        return None

if __name__ == "__main__":
    try:
        # ニュース収集実行
        news_data = collect_crypto_news()
        
        if news_data:
            # データ保存
            saved_file = save_news_data(news_data)
            
            print("\n🎉 ニュース収集完了！")
            print(f"次のステップ: これらのニュースから記事を生成できます")
            
            # 記事生成の準備ができているニュースを表示
            high_priority_news = [n for n in news_data if n['importance_score'] >= 70]
            medium_priority_news = [n for n in news_data if 50 <= n['importance_score'] < 70]
            
            print(f"\n📝 高優先度記事（70点以上）: {len(high_priority_news)}件")
            print(f"📝 中優先度記事（50-69点）: {len(medium_priority_news)}件")
            
            if high_priority_news:
                print("\n🔥 高優先度ニュース:")
                for i, news in enumerate(high_priority_news[:5], 1):
                    print(f"  {i}. [{news['source']}] {news['title'][:80]}...")
                    print(f"     重要度: {news['importance_score']:.1f}/100")
            
            total_quality_news = len(high_priority_news) + len(medium_priority_news)
            print(f"\n✨ 合計 {total_quality_news} 件の高品質ニュースを収集しました！")
            
        else:
            print("❌ ニュースが取得できませんでした")
            
    except KeyboardInterrupt:
        print("\n⚠️ 処理が中断されました")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)