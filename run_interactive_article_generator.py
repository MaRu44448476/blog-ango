#!/usr/bin/env python3
"""
対話型記事生成システム（親しみやすい日本語版）
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
    """英語タイトルを日本語風に翻訳（簡易版）"""
    # よく使われる仮想通貨用語の翻訳マップ
    translations = {
        'BTC': 'ビットコイン',
        'Bitcoin': 'ビットコイン',
        'ETH': 'イーサリアム',
        'Ethereum': 'イーサリアム',
        'leads': 'がリード',
        'majors': '主要通貨',
        'soar': 'が急上昇',
        'soars': 'が急上昇',
        'hits ATH': 'が過去最高値更新',
        'hits new high': 'が新高値更新',
        'stable': 'は安定推移',
        'ahead of': 'を前に',
        'coming soon': 'が間もなく登場',
        'rebounds': 'が反発',
        'after': 'の後',
        'conflict': '紛争',
        'edges higher': 'が小幅上昇',
        'reduces': 'を削減',
        'stake': '保有比率',
        'delayed': 'が延期',
        'plunges': 'が急落',
        'strikes': 'が攻撃',
        'Gold': '金',
        'Oil': '原油',
        'rally fails': 'の上昇が失速',
        'tensions grow': 'の緊張が高まる',
        'treasuries': '国債',
        'expects': 'が予想',
        'to hit': 'に到達すると',
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
        'pump': 'の急騰',
        'crash': 'の暴落',
        'NFT': 'NFT',
        'staking': 'ステーキング',
        'mining': 'マイニング'
    }
    
    # 大文字小文字を区別しない置換
    translated = title
    for eng, jpn in translations.items():
        # 正規表現で単語境界を考慮して置換
        pattern = r'\b' + re.escape(eng) + r'\b'
        translated = re.sub(pattern, jpn, translated, flags=re.IGNORECASE)
    
    # 残った英語の記号を日本語に
    translated = translated.replace(',', '、')
    translated = translated.replace('&', 'と')
    
    return translated

def display_article_candidates(news_items):
    """記事候補を表示"""
    print("📝 記事作成候補のニュース一覧")
    print("=" * 80)
    
    # 重要度でソートして上位20件を表示
    sorted_news = sorted(news_items, key=lambda x: x['importance_score'], reverse=True)[:20]
    
    candidates = []
    for i, news in enumerate(sorted_news, 1):
        # タイトルを日本語化
        original_title = news['title']
        japanese_title = translate_title_to_japanese(original_title)
        
        print(f"\n【候補 {i}】")
        print(f"📰 元タイトル: {original_title}")
        print(f"🇯🇵 日本語タイトル案: {japanese_title}")
        print(f"📊 重要度: ★{'★' * int(news['importance_score'] / 20)}☆{'☆' * (5 - int(news['importance_score'] / 20))} ({news['importance_score']:.1f}/100)")
        print(f"📡 ソース: {news['source']}")
        
        # 内容の要約（最初の100文字）
        if news.get('description'):
            desc = news['description'][:100] + "..." if len(news['description']) > 100 else news['description']
            print(f"📄 概要: {desc}")
        
        # おすすめ度を判定
        recommendation = ""
        if news['importance_score'] >= 70:
            recommendation = "🔥 非常におすすめ！市場に大きな影響がありそうです"
        elif news['importance_score'] >= 50:
            recommendation = "👍 おすすめ！多くの投資家が注目しそうです"
        elif news['importance_score'] >= 30:
            recommendation = "📌 検討の価値あり。特定の層に響きそうです"
        else:
            recommendation = "💡 ニッチな話題。専門的な読者向けかも"
        
        print(f"💭 おすすめ度: {recommendation}")
        
        candidates.append({
            'index': i,
            'news': news,
            'japanese_title': japanese_title,
            'recommendation': recommendation
        })
    
    print("\n" + "=" * 80)
    print("\n💡 ヒント:")
    print("- 重要度が高いニュースは多くの読者の関心を引きやすいです")
    print("- ビットコインやイーサリアム関連は安定した人気があります")
    print("- 規制や政府関連のニュースは長期的な影響を与える可能性があります")
    print("- DeFiやNFTは最新トレンドに敏感な読者に人気です")
    
    return candidates

def generate_friendly_article(news_item, japanese_title):
    """親しみやすい日本語で記事を生成"""
    
    now = datetime.now()
    
    # タイトルをより親しみやすく
    title = f"【解説】{japanese_title}ってどういうこと？初心者にもわかりやすく説明します"
    
    # 内容も親しみやすい文体で
    content = f"""
<h2>今回のニュースをざっくり説明すると...</h2>
<p>みなさん、こんにちは！今日は仮想通貨界隈でちょっと話題になっているニュースについて、できるだけわかりやすく解説していきたいと思います。</p>

<p>今回のニュースを一言でまとめると、「<strong>{japanese_title}</strong>」ということなんですが、これだけだと「で、それって何？」って感じですよね。もう少し詳しく見ていきましょう！</p>

<h2>どんな内容なの？</h2>
<p>このニュースは{news_item['source']}から報じられたもので、仮想通貨市場にとってはなかなか重要な話題なんです。</p>

<p>具体的には、{news_item.get('description', 'このニュースの詳細な内容')[:150]}...という感じの内容になっています。</p>

<h3>なぜこれが重要なの？</h3>
"""
    
    # 重要度に応じた解説
    if news_item['importance_score'] >= 70:
        content += """
<p>このニュースがなぜ重要かというと、<strong>市場全体に大きな影響を与える可能性が高い</strong>からなんです。</p>

<p>例えば、あなたがビットコインやイーサリアムを持っているなら、このニュースによって価格が大きく動く可能性があります。「えっ、じゃあ今すぐ何かした方がいいの？」と思うかもしれませんが、まずは落ち着いて状況を見守ることが大切です。</p>
"""
    elif news_item['importance_score'] >= 50:
        content += """
<p>このニュースは、<strong>仮想通貨市場の今後の流れを読む上で重要な手がかり</strong>になりそうです。</p>

<p>すぐに何か大きな変化があるわけではないかもしれませんが、中長期的に見ると、投資判断の参考になる情報だと思います。「へぇ〜、そんなことが起きてるんだ」くらいの気持ちで頭の片隅に置いておくといいかもしれません。</p>
"""
    else:
        content += """
<p>このニュースは、<strong>特定の分野や通貨に興味がある人にとって参考になる情報</strong>です。</p>

<p>市場全体への影響は限定的かもしれませんが、関連する仮想通貨やプロジェクトに投資している人は要チェックですね。「自分には関係ないかな」と思っても、仮想通貨の世界では思わぬところでつながっていることもあるので、知っておいて損はないと思います。</p>
"""
    
    # キーワード解説
    keywords = []
    title_lower = news_item['title'].lower()
    if 'bitcoin' in title_lower or 'btc' in title_lower:
        keywords.append(('ビットコイン', '仮想通貨の代表格。デジタルゴールドとも呼ばれています'))
    if 'ethereum' in title_lower or 'eth' in title_lower:
        keywords.append(('イーサリアム', 'スマートコントラクトが使える仮想通貨プラットフォーム'))
    if 'defi' in title_lower:
        keywords.append(('DeFi（ディーファイ）', '銀行などを介さない分散型の金融サービス'))
    if 'nft' in title_lower:
        keywords.append(('NFT', 'デジタルアートなどの所有権を証明する技術'))
    if 'regulation' in title_lower or 'sec' in title_lower:
        keywords.append(('規制', '政府や当局による仮想通貨のルール作り'))
    
    if keywords:
        content += """
<h2>ちょっと難しい言葉の解説</h2>
<p>この記事に出てくる専門用語について、簡単に説明しますね：</p>
<ul>
"""
        for keyword, explanation in keywords:
            content += f"<li><strong>{keyword}</strong>：{explanation}</li>\n"
        
        content += "</ul>\n"
    
    content += f"""
<h2>で、結局どうすればいいの？</h2>
<p>このニュースを受けて、私たち個人投資家はどう動けばいいのでしょうか？</p>

<p>正直なところ、<strong>慌てて何かをする必要はありません</strong>。仮想通貨投資で大切なのは、情報をしっかり集めて、冷静に判断することです。</p>

<p>もしあなたが仮想通貨を持っているなら：</p>
<ul>
<li>このニュースが自分の持っている通貨にどう影響するか考えてみる</li>
<li>投資金額は無理のない範囲で</li>
<li>長期的な視点を忘れずに</li>
</ul>

<p>まだ仮想通貨を持っていない方も、こういったニュースを追っていくことで、市場の流れが少しずつわかってくると思います。</p>

<h2>まとめ</h2>
<p>今回は「{japanese_title}」というニュースについて解説しました。</p>

<p>仮想通貨の世界は日々新しいニュースが飛び交っていて、ついていくのが大変かもしれません。でも、一つ一つのニュースを理解していくことで、少しずつこの世界のことがわかってくるはずです。</p>

<p>これからも、みなさんにとってわかりやすい形で仮想通貨の情報をお届けしていきたいと思います。最後まで読んでいただき、ありがとうございました！</p>

<hr>
<p><small>📌 元記事：<a href="{news_item['url']}" target="_blank" rel="noopener">{news_item['source']}（英語）</a></small></p>
<p><small>⚠️ この記事は情報提供を目的としています。投資は自己責任でお願いします。</small></p>
<p><small>📅 記事作成日：{now.strftime('%Y年%m月%d日')}</small></p>
"""
    
    # 文字数計算
    word_count = len(content.replace(' ', '').replace('\n', '').replace('<', '').replace('>', ''))
    
    article = {
        'title': title,
        'content': content,
        'word_count': word_count,
        'article_type': 'news_friendly',
        'category': 'ニュース解説',
        'tags': ['仮想通貨', '初心者向け', 'わかりやすい解説'] + ([k[0] for k in keywords]),
        'generation_date': now.isoformat(),
        'original_title': news_item['title'],
        'japanese_title': japanese_title,
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
        
        print(f"💾 記事を保存しました: {filename}")
        return filename
    except Exception as e:
        print(f"❌ 記事保存エラー: {e}")
        return None

def main():
    """メイン実行"""
    print("🚀 対話型記事生成システム（親しみやすい日本語版）")
    print("=" * 80)
    
    # ニュースデータを読み込み
    news_items = load_latest_news()
    if not news_items:
        return
    
    # 記事候補を表示
    candidates = display_article_candidates(news_items)
    
    print("\n📝 どのニュースについて記事を書きますか？")
    print("番号を入力してください（1-20）: ", end="")
    
    try:
        # ClaudeCode環境では入力ができないので、デフォルトで1番を選択
        choice = 1
        print(f"{choice}")  # 選択した番号を表示
        
        if 1 <= choice <= len(candidates):
            selected = candidates[choice - 1]
            news_item = selected['news']
            japanese_title = selected['japanese_title']
            
            print(f"\n✅ 選択されたニュース: {japanese_title}")
            print("✍️ 親しみやすい日本語で記事を生成中...")
            
            # 記事生成
            article = generate_friendly_article(news_item, japanese_title)
            
            # プレビュー表示
            print("\n" + "=" * 80)
            print("📝 生成された記事のプレビュー")
            print("=" * 80)
            print(f"タイトル: {article['title']}")
            print(f"文字数: {article['word_count']}字")
            print(f"カテゴリ: {article['category']}")
            print(f"タグ: {', '.join(article['tags'])}")
            print("\n--- 記事の冒頭 ---")
            print(article['content'][:500] + "...")
            print("=" * 80)
            
            # 保存
            save_article(article)
            
            print("\n🎉 記事生成が完了しました！")
            print("次のステップ: python3 run_wordpress_publish.py で投稿できます")
            
        else:
            print("❌ 無効な番号です")
            
    except ValueError:
        print("❌ 数字を入力してください")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    main()