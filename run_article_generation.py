#!/usr/bin/env python3
"""
記事生成実行スクリプト
"""

import json
import sys
from datetime import datetime
import urllib.request
import base64

def load_latest_news():
    """最新のニュースデータを読み込み"""
    import glob
    import os
    
    # collected_news_*.jsonファイルを探す
    news_files = glob.glob("collected_news_*.json")
    
    if not news_files:
        print("❌ ニュースデータが見つかりません")
        print("まず run_news_collection.py を実行してください")
        return None
    
    # 最新のファイルを取得
    latest_file = max(news_files, key=os.path.getctime)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📰 ニュースデータを読み込み: {latest_file}")
        print(f"📊 ニュース件数: {data['total_count']}件")
        
        return data['news_items']
    except Exception as e:
        print(f"❌ ニュースデータ読み込みエラー: {e}")
        return None

def generate_weekly_summary_article(news_items):
    """週刊まとめ記事を生成"""
    
    # 重要度の高いニュースを選択（上位5件）
    top_news = sorted(news_items, key=lambda x: x['importance_score'], reverse=True)[:5]
    
    # 記事作成
    now = datetime.now()
    title = f"【週刊仮想通貨レポート】{now.month}月{now.day}日週の重要ニュースまとめ"
    
    content = f"""
<h2>今週の仮想通貨市場概況</h2>
<p>今週の仮想通貨市場は、{len(news_items)}件の重要なニュースが報じられました。市場全体の動向を見ると、ビットコインやイーサリアムなどの主要通貨を中心とした動きが注目されています。</p>

<h2>今週の注目ニュース</h2>
"""
    
    for i, news in enumerate(top_news, 1):
        content += f"""
<h3>{i}. {news['title']}</h3>
<p><strong>ソース:</strong> {news['source']}</p>
<p>{news['description']}</p>
<p><strong>重要度:</strong> {news['importance_score']:.1f}/100</p>
<p><a href="{news['url']}" target="_blank">詳細を読む</a></p>
"""
    
    content += f"""
<h2>市場分析</h2>
<p>今週収集されたニュースを分析すると、以下のような傾向が見られます：</p>
<ul>
<li>重要度50以上のニュース: {len([n for n in news_items if n['importance_score'] >= 50])}件</li>
<li>ビットコイン関連: {len([n for n in news_items if 'bitcoin' in n['title'].lower() or 'btc' in n['title'].lower()])}件</li>
<li>イーサリアム関連: {len([n for n in news_items if 'ethereum' in n['title'].lower() or 'eth' in n['title'].lower()])}件</li>
<li>規制関連: {len([n for n in news_items if 'regulation' in n['title'].lower() or '規制' in n['title']])}件</li>
</ul>

<h2>来週の注目ポイント</h2>
<p>来週は引き続き主要通貨の動向に注目が集まりそうです。特に、今週報じられたニュースの後続展開や新たな規制動向、企業の仮想通貨採用ニュースなどが市場に影響を与える可能性があります。</p>

<hr>
<p><small>※本記事は収集されたニュースを基に自動生成されたものです。投資判断は自己責任でお願いします。</small></p>
<p><small>📊 分析対象ニュース: {len(news_items)}件 | 生成日時: {now.strftime('%Y年%m月%d日 %H時%M分')}</small></p>
"""
    
    # 文字数計算
    word_count = len(content.replace(' ', '').replace('\n', '').replace('<', '').replace('>', ''))
    
    article = {
        'title': title,
        'content': content,
        'word_count': word_count,
        'article_type': 'weekly_summary',
        'category': '週刊まとめ',
        'tags': ['仮想通貨', '週刊レポート', '市場分析', 'ビットコイン', 'イーサリアム'],
        'generation_date': now.isoformat(),
        'source_news_count': len(news_items),
        'top_news_count': len(top_news)
    }
    
    return article

def generate_news_article(news_item):
    """個別ニュース記事を生成"""
    
    title = f"【仮想通貨ニュース】{news_item['title']}"
    
    content = f"""
<h2>ニュース概要</h2>
<p>{news_item['description']}</p>

<h2>詳細分析</h2>
<p>このニュースは{news_item['source']}から報じられたもので、仮想通貨市場における重要な動向の一つとして注目されています。</p>

<h3>市場への影響</h3>
<p>重要度{news_item['importance_score']:.1f}/100のこのニュースは、"""
    
    # 重要度に応じたコメント
    if news_item['importance_score'] >= 70:
        content += "非常に高い注目度を持ち、市場全体に大きな影響を与える可能性があります。"
    elif news_item['importance_score'] >= 50:
        content += "高い注目度を持ち、関連する仮想通貨や市場セグメントに影響を与える可能性があります。"
    else:
        content += "一定の注目度を持ち、特定の領域や投資家層に影響を与える可能性があります。"
    
    content += "</p>"
    
    # キーワード分析
    keywords = []
    title_lower = news_item['title'].lower()
    if 'bitcoin' in title_lower or 'btc' in title_lower:
        keywords.append('ビットコイン')
    if 'ethereum' in title_lower or 'eth' in title_lower:
        keywords.append('イーサリアム')
    if 'defi' in title_lower:
        keywords.append('DeFi')
    if 'nft' in title_lower:
        keywords.append('NFT')
    if 'regulation' in title_lower:
        keywords.append('規制')
    
    if keywords:
        content += f"""
<h3>関連キーワード</h3>
<p>このニュースは特に以下の分野に関連しています: {', '.join(keywords)}</p>
"""
    
    content += f"""
<h2>まとめ</h2>
<p>今回の{news_item['source']}からの報道は、仮想通貨業界の動向を理解する上で重要な情報となります。引き続き関連する動向に注目していく必要があります。</p>

<h3>元記事</h3>
<p><a href="{news_item['url']}" target="_blank">{news_item['source']}で詳細を読む</a></p>

<hr>
<p><small>※本記事は{news_item['source']}のニュースを基に自動生成されたものです。投資判断は自己責任でお願いします。</small></p>
<p><small>📰 ソース: {news_item['source']} | 生成日時: {datetime.now().strftime('%Y年%m月%d日 %H時%M分')}</small></p>
"""
    
    # 文字数計算
    word_count = len(content.replace(' ', '').replace('\n', '').replace('<', '').replace('>', ''))
    
    article = {
        'title': title,
        'content': content,
        'word_count': word_count,
        'article_type': 'news',
        'category': 'ニュース',
        'tags': ['仮想通貨', 'ニュース'] + keywords,
        'generation_date': datetime.now().isoformat(),
        'original_source': news_item['source'],
        'original_url': news_item['url'],
        'importance_score': news_item['importance_score']
    }
    
    return article

def save_article(article):
    """記事をJSONファイルに保存"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"generated_article_{article['article_type']}_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        
        print(f"💾 記事を保存: {filename}")
        return filename
    except Exception as e:
        print(f"❌ 記事保存エラー: {e}")
        return None

def preview_article(article):
    """記事をプレビュー表示"""
    print("\n" + "="*60)
    print("📝 生成された記事のプレビュー")
    print("="*60)
    print(f"タイトル: {article['title']}")
    print(f"文字数: {article['word_count']}字")
    print(f"カテゴリ: {article['category']}")
    print(f"タグ: {', '.join(article['tags'])}")
    print(f"記事タイプ: {article['article_type']}")
    print("\n--- 記事内容 ---")
    print(article['content'][:500] + "..." if len(article['content']) > 500 else article['content'])
    print("="*60)

def main():
    """メイン実行"""
    print("🚀 仮想通貨記事生成システム")
    print("="*50)
    
    # ニュースデータを読み込み
    news_items = load_latest_news()
    if not news_items:
        return
    
    print("\n📝 記事生成オプション:")
    print("1. 週刊まとめ記事を生成")
    print("2. 重要ニュース記事を生成")
    print("3. 両方生成")
    
    try:
        choice = "1"  # デフォルトで週刊まとめを生成
        
        if choice in ["1", "3"]:
            print("\n✍️ 週刊まとめ記事を生成中...")
            weekly_article = generate_weekly_summary_article(news_items)
            preview_article(weekly_article)
            save_article(weekly_article)
            
            print(f"\n✅ 週刊まとめ記事生成完了！")
            print(f"📊 {weekly_article['word_count']}字の記事を生成しました")
        
        if choice in ["2", "3"]:
            # 重要度の高いニュースを選択
            high_priority_news = [n for n in news_items if n['importance_score'] >= 50]
            
            if high_priority_news:
                print(f"\n✍️ 重要ニュース記事を生成中... ({len(high_priority_news)}件)")
                
                for i, news in enumerate(high_priority_news[:3], 1):  # 上位3件まで
                    print(f"\n--- 記事 {i}/{min(3, len(high_priority_news))} ---")
                    news_article = generate_news_article(news)
                    preview_article(news_article)
                    save_article(news_article)
                    
                print(f"\n✅ 重要ニュース記事生成完了！")
            else:
                print("\n⚠️ 重要度50以上のニュースがありません")
        
        print("\n🎉 記事生成が完了しました！")
        print("次のステップ: 生成された記事をWordPressに投稿できます")
        print("投稿するには: python3 run_wordpress_publish.py")
        
    except Exception as e:
        print(f"❌ 記事生成エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()