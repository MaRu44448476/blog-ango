#!/usr/bin/env python3
"""
記事候補提示システム（選択式）
"""

import json
import sys
import glob
import os
from datetime import datetime
import re

def load_latest_news():
    """最新のニュースデータを読み込み"""
    news_files = glob.glob("collected_news_*.json")
    
    if not news_files:
        print("❌ ニュースデータが見つかりません")
        print("まず run_news_collection.py を実行してください")
        return None
    
    latest_file = max(news_files, key=os.path.getctime)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📰 ニュースデータを読み込みました: {latest_file}")
        print(f"📊 合計{data['total_count']}件のニュースがあります\n")
        
        return data['news_items']
    except Exception as e:
        print(f"❌ ニュースデータ読み込みエラー: {e}")
        return None

def translate_title_to_japanese(title):
    """英語タイトルを日本語風に翻訳（改良版）"""
    translations = {
        'BTC': 'ビットコイン',
        'Bitcoin': 'ビットコイン', 
        'ETH': 'イーサリアム',
        'Ethereum': 'イーサリアム',
        'SOL': 'ソラナ',
        'Solana': 'ソラナ',
        'XRP': 'リップル',
        'ADA': 'カルダノ',
        'DOGE': 'ドージコイン',
        'leads': 'がリード',
        'majors': '主要通貨',
        'soar': '急上昇',
        'soars': '急上昇',
        'hits ATH': '過去最高値更新',
        'hits new high': '新高値更新',
        'stable': '安定推移',
        'steady': '安定',
        'ahead of': 'を前に',
        'coming soon': '間もなく登場',
        'rebounds': '反発',
        'after': '後',
        'edges higher': '小幅上昇',
        'reduces': '削減',
        'delayed': '延期',
        'plunges': '急落',
        'falls': '下落',
        'strikes': '攻撃',
        'rally fails': '上昇失速',
        'tensions grow': '緊張高まる',
        'expects': '予想',
        'to hit': '到達予測',
        'new highs': '新高値',
        'CRYPTO': '仮想通貨',
        'cryptocurrency': '仮想通貨',
        'DeFi': 'DeFi（分散型金融）',
        'coins': 'コイン',
        'token': 'トークン',
        'SEC': 'SEC（米証券取引委員会）',
        'regulation': '規制',
        'government': '政府',
        'exchange': '取引所',
        'trading': 'トレード',
        'price': '価格',
        'market': '市場',
        'ETF': 'ETF',
        'ETFs': 'ETF',
        'staking': 'ステーキング',
        'mining': 'マイニング',
        'Gold': '金',
        'Oil': '原油',
        'stocks': '株式',
        'pumps': '急騰',
        'pump': '急騰',
        'crash': '暴落',
        'approves': '承認',
        'secures': '調達',
        'boost': '増強'
    }
    
    translated = title
    for eng, jpn in translations.items():
        pattern = r'\b' + re.escape(eng) + r'\b'
        translated = re.sub(pattern, jpn, translated, flags=re.IGNORECASE)
    
    translated = translated.replace(',', '、')
    translated = translated.replace('&', 'と')
    translated = translated.replace('$', '')
    
    return translated

def categorize_news_type(news_item):
    """ニュースの種類を分類"""
    title = news_item['title'].lower()
    content = news_item.get('description', '').lower()
    text = title + ' ' + content
    
    categories = []
    
    if any(word in text for word in ['price', 'hits', 'surge', 'soar', 'plunge', 'crash', '$', 'ath', 'high']):
        categories.append('💰 価格・相場')
    
    if any(word in text for word in ['regulation', 'sec', 'government', 'legal', 'approve', 'ban']):
        categories.append('⚖️ 規制・政策')
    
    if any(word in text for word in ['etf', 'fund', 'institutional', 'investment', 'treasury']):
        categories.append('🏦 機関投資')
    
    if any(word in text for word in ['defi', 'yield', 'liquidity', 'staking', 'protocol']):
        categories.append('🔗 DeFi・プロトコル')
    
    if any(word in text for word in ['nft', 'collectible', 'art', 'gaming']):
        categories.append('🎨 NFT・ゲーム')
    
    if any(word in text for word in ['exchange', 'trading', 'platform', 'listing']):
        categories.append('🏢 取引所・プラットフォーム')
    
    if any(word in text for word in ['partnership', 'adoption', 'integration', 'corporate']):
        categories.append('🤝 企業・提携')
    
    if any(word in text for word in ['technology', 'upgrade', 'fork', 'consensus', 'blockchain']):
        categories.append('⚙️ 技術・開発')
    
    if any(word in text for word in ['hack', 'security', 'breach', 'exploit', 'vulnerability']):
        categories.append('🔐 セキュリティ')
    
    if any(word in text for word in ['market', 'macro', 'economic', 'fed', 'inflation', 'geopolitical']):
        categories.append('📊 マクロ経済')
    
    return categories if categories else ['📰 一般ニュース']

def estimate_reader_interest(news_item):
    """読者興味度を推定"""
    title = news_item['title'].lower()
    importance = news_item.get('importance_score', 0)
    
    # 基本興味度
    interest_score = importance
    
    # 日本人に人気のトピック
    if any(word in title for word in ['bitcoin', 'btc']):
        interest_score += 15
    if any(word in title for word in ['ethereum', 'eth']):
        interest_score += 10
    if any(word in title for word in ['price', '$', 'yen', 'surge', 'crash']):
        interest_score += 10
    if any(word in title for word in ['japan', 'japanese', 'asia']):
        interest_score += 20
    if any(word in title for word in ['regulation', 'government']):
        interest_score += 8
    if any(word in title for word in ['etf', 'institutional']):
        interest_score += 12
    
    # マイナス要因
    if any(word in title for word in ['technical', 'fork', 'consensus', 'node']):
        interest_score -= 5
    if len(title.split()) > 15:  # 長すぎるタイトル
        interest_score -= 3
    
    return min(interest_score, 100)

def create_article_pitch(news_item, japanese_title):
    """記事の魅力をアピールする文章を作成"""
    categories = categorize_news_type(news_item)
    interest_score = estimate_reader_interest(news_item)
    importance = news_item.get('importance_score', 0)
    
    pitches = []
    
    # 重要度に応じたアピール
    if importance >= 70:
        pitches.append("🔥 超話題！多くのメディアが注目している重要ニュースです")
    elif importance >= 50:
        pitches.append("📈 注目度高！投資家が気にしている情報です")
    elif importance >= 30:
        pitches.append("💡 知っておくべき！業界の動向がわかります")
    else:
        pitches.append("📚 豆知識として！マニアックな話題です")
    
    # カテゴリに応じたアピール
    if '💰 価格・相場' in categories:
        pitches.append("💰 価格に直接影響する可能性があり、投資判断の参考になります")
    
    if '⚖️ 規制・政策' in categories:
        pitches.append("⚖️ 長期的な市場への影響が大きく、今後の動向を占う重要な材料です")
    
    if '🏦 機関投資' in categories:
        pitches.append("🏦 大口投資家の動向がわかり、市場の流れを読むのに役立ちます")
    
    if '🔗 DeFi・プロトコル' in categories:
        pitches.append("🔗 最新のDeFiトレンドがわかり、技術的な理解が深まります")
    
    # 読者興味度に応じたコメント
    if interest_score >= 80:
        pitches.append("👥 多くの日本人読者が関心を持ちそうな内容です")
    elif interest_score >= 60:
        pitches.append("🎯 仮想通貨投資家なら知っておきたい情報です")
    elif interest_score >= 40:
        pitches.append("🤔 やや専門的ですが、詳しい人には刺さる内容です")
    else:
        pitches.append("📖 ニッチですが、特定の読者層には価値ある情報です")
    
    return pitches

def suggest_article_angle(news_item, japanese_title):
    """記事の切り口を提案"""
    title = news_item['title'].lower()
    categories = categorize_news_type(news_item)
    
    angles = []
    
    if '💰 価格・相場' in categories:
        if 'surge' in title or 'soar' in title or 'pump' in title:
            angles.append("📊 「なぜ急上昇？」価格上昇の背景を初心者向けに解説")
        elif 'crash' in title or 'plunge' in title or 'fall' in title:
            angles.append("📉 「何が起きた？」価格下落の原因と今後の見通し")
        else:
            angles.append("💹 「投資家必見」価格動向の分析と注意点")
    
    if '⚖️ 規制・政策' in categories:
        angles.append("🏛️ 「どう影響する？」規制ニュースを日本の投資家目線で解説")
    
    if '🏦 機関投資' in categories:
        angles.append("🏢 「大手が動いた！」機関投資家の動向が個人投資家に与える影響")
    
    if '🔗 DeFi・プロトコル' in categories:
        angles.append("⚙️ 「最新技術解説」DeFi初心者でもわかる仕組みと可能性")
    
    if any(word in title for word in ['bitcoin', 'btc']):
        angles.append("₿ 「ビットコイン特集」今回のニュースが長期トレンドに与える影響")
    
    if any(word in title for word in ['ethereum', 'eth']):
        angles.append("🔷 「イーサリアム解説」技術的なアップデートをわかりやすく説明")
    
    # デフォルトの切り口
    if not angles:
        angles.append("📰 「今話題の仮想通貨ニュース」初心者にもわかりやすく解説")
    
    return angles

def display_article_candidates(news_items, limit=10):
    """記事候補を表示（選択式）"""
    print("🎯 記事作成候補の提案")
    print("=" * 100)
    print("以下の中から、どのニュースで記事を作成しますか？\n")
    
    # 重要度と興味度でソート
    def score_news(news):
        return (news.get('importance_score', 0) * 0.6 + 
                estimate_reader_interest(news) * 0.4)
    
    sorted_news = sorted(news_items, key=score_news, reverse=True)[:limit]
    
    candidates = []
    for i, news in enumerate(sorted_news, 1):
        japanese_title = translate_title_to_japanese(news['title'])
        categories = categorize_news_type(news)
        interest_score = estimate_reader_interest(news)
        pitches = create_article_pitch(news, japanese_title)
        angles = suggest_article_angle(news, japanese_title)
        
        print(f"【候補 {i}】")
        print(f"🌐 元タイトル: {news['title']}")
        print(f"🇯🇵 日本語タイトル案: {japanese_title}")
        print(f"📂 カテゴリ: {' '.join(categories)}")
        print(f"📊 重要度: {news.get('importance_score', 0):.1f}/100")
        print(f"👥 読者興味度: {interest_score:.1f}/100")
        print(f"📡 ソース: {news['source']}")
        
        # 概要（短縮版）
        if news.get('description'):
            desc = news['description'][:80] + "..." if len(news['description']) > 80 else news['description']
            print(f"📄 概要: {desc}")
        
        print("💡 なぜおすすめ？")
        for pitch in pitches:
            print(f"   {pitch}")
        
        print("✍️ 記事の切り口案:")
        for angle in angles[:2]:  # 上位2つまで
            print(f"   {angle}")
        
        # 推奨度の総合判定
        total_score = (news.get('importance_score', 0) + interest_score) / 2
        if total_score >= 70:
            print("🔥 ★★★ 非常におすすめ！確実にバズりそうです")
        elif total_score >= 50:
            print("👍 ★★☆ おすすめ！多くの読者が興味を持ちそうです")
        elif total_score >= 30:
            print("📝 ★☆☆ 検討の価値あり。特定の読者には刺さりそうです")
        else:
            print("💭 ☆☆☆ ニッチな話題。マニア向けかもしれません")
        
        print("-" * 100)
        
        candidates.append({
            'index': i,
            'news': news,
            'japanese_title': japanese_title,
            'categories': categories,
            'interest_score': interest_score,
            'pitches': pitches,
            'angles': angles,
            'total_score': total_score
        })
    
    print("\n🎯 選択のヒント:")
    print("★★★ = 確実に読まれる、シェアされやすい")
    print("★★☆ = 安定した人気が見込める")
    print("★☆☆ = コアなファンには刺さる")
    print("☆☆☆ = チャレンジングだが差別化できる")
    
    print("\n💡 記事作成時のアドバイス:")
    print("• 価格関連は即時性が重要です")
    print("• 規制ニュースは長期的な視点で解説しましょう")
    print("• 技術的な内容は図解やたとえ話を使うと理解しやすくなります")
    print("• 日本人読者には「どう影響するか」の視点が人気です")
    
    return candidates

def save_selected_candidates(candidates):
    """候補データを保存"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"article_candidates_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_candidates': len(candidates),
                'candidates': candidates
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 候補データを保存しました: {filename}")
        return filename
    except Exception as e:
        print(f"❌ 候補データ保存エラー: {e}")
        return None

def main():
    """メイン実行"""
    print("🚀 記事候補提示システム")
    print("=" * 100)
    
    # ニュースデータを読み込み
    news_items = load_latest_news()
    if not news_items:
        return
    
    # 記事候補を表示
    candidates = display_article_candidates(news_items, limit=10)
    
    # 候補データを保存
    save_selected_candidates(candidates)
    
    print("\n📝 記事を作成するには:")
    print("1. 上記の候補から番号を選んでください")
    print("2. run_selected_article_generator.py [番号] で記事生成")
    print("   例: python3 run_selected_article_generator.py 1")
    print("\n🔄 新しいニュースで候補を更新:")
    print("python3 run_news_collection.py && python3 show_article_candidates.py")

if __name__ == "__main__":
    main()