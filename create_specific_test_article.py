#!/usr/bin/env python3
"""
特定のテスト記事を作成（スタンダードチャータード銀行のビットコイン価格予想）
"""

import json
from datetime import datetime

def create_test_article():
    """親しみやすい日本語でテスト記事を生成"""
    
    now = datetime.now()
    
    title = "【話題】大手銀行がビットコイン価格「13万5000ドル」予想！？これって本当に実現するの？"
    
    content = """
<h2>今回のニュースをざっくり説明すると...</h2>
<p>みなさん、こんにちは！今日は仮想通貨界隈でかなり話題になっているビッグニュースについて、できるだけわかりやすく解説していきたいと思います。</p>

<p>なんと、世界的な大手銀行である<strong>スタンダードチャータード銀行</strong>が、「ビットコインの価格が2025年第3四半期（7〜9月）に<strong>13万5000ドル（約2100万円）</strong>に達する可能性がある」と予想したんです！</p>

<p>「えっ、今のビットコイン価格って10万ドルくらいでしょ？本当にそんなに上がるの？」って思いますよね。私も最初聞いたときは「マジで！？」って思いました。詳しく見ていきましょう！</p>

<h2>スタンダードチャータード銀行ってどんな銀行？</h2>
<p>まず、この予想を出した銀行について簡単に説明しますね。スタンダードチャータード銀行は、イギリスに本社がある国際的な大手銀行で、特にアジアや中東、アフリカなどの新興市場に強いんです。</p>

<p>つまり、<strong>そこら辺の怪しい予想屋さんではなく、ちゃんとした金融機関</strong>が出した予想ということ。これは注目せざるを得ませんよね！</p>

<h2>なぜ13万5000ドルという予想が出たの？</h2>
<p>銀行がこんな強気な予想を出した理由はいくつかあるようです：</p>

<h3>1. 機関投資家の参入が加速</h3>
<p>最近、大手企業や投資ファンドがどんどんビットコインを買い始めています。「デジタルゴールド」として資産の一部をビットコインで持とうという動きが広がっているんです。</p>

<h3>2. ビットコインETFの普及</h3>
<p>アメリカでビットコインETF（上場投資信託）が承認されて、一般の投資家も簡単にビットコインに投資できるようになりました。これが価格を押し上げる要因になっているそうです。</p>

<h3>3. 半減期後の価格上昇パターン</h3>
<p>ビットコインには4年に1度「半減期」という、新規発行量が半分になるイベントがあります。過去のデータを見ると、半減期の後は価格が大きく上昇する傾向があるんです。</p>

<h2>でも、ちょっと待って！リスクもあるよね？</h2>
<p>もちろん、いいことばかりではありません。仮想通貨投資にはリスクもつきものです：</p>

<ul>
<li><strong>価格の激しい変動</strong>：1日で10%以上動くこともざら</li>
<li><strong>規制リスク</strong>：各国政府の規制によって大きく影響を受ける</li>
<li><strong>技術的なリスク</strong>：ハッキングや取引所の問題など</li>
</ul>

<p>「じゃあ、どうすればいいの？」って思いますよね。</p>

<h2>私たち個人投資家はどう考えるべき？</h2>
<p>正直なところ、<strong>予想は予想</strong>です。必ず当たるわけではありません。でも、大手銀行がこういう予想を出すということは、それだけビットコインが「まともな投資対象」として認められてきた証拠でもあります。</p>

<h3>もしビットコインに興味があるなら...</h3>
<ol>
<li><strong>少額から始める</strong>：いきなり大金を投じるのはNG！</li>
<li><strong>長期的な視点を持つ</strong>：短期の値動きに一喜一憂しない</li>
<li><strong>余裕資金で投資する</strong>：生活費を投資に回すのは絶対ダメ</li>
<li><strong>分散投資を心がける</strong>：ビットコインだけに全財産を賭けない</li>
</ol>

<h2>まとめ：夢は大きく、でも現実的に</h2>
<p>スタンダードチャータード銀行の「ビットコイン13万5000ドル予想」は確かに夢のある話です。もし本当にそうなったら、今から投資しておけば資産が1.3倍以上になる計算ですからね。</p>

<p>でも、<strong>投資は自己責任</strong>。予想が外れることだってあります。大切なのは、しっかりと情報を集めて、自分で判断すること。そして、無理のない範囲で楽しむことです。</p>

<p>仮想通貨の世界はまだまだ発展途上。これからも色んなニュースが飛び込んでくると思います。一緒に学びながら、この新しい金融の世界を楽しんでいきましょう！</p>

<p>今日も最後まで読んでいただき、ありがとうございました。また次回の記事でお会いしましょう！</p>

<hr>
<p><small>📌 参考情報：この記事は2025年1月のニュースを基に作成されています</small></p>
<p><small>⚠️ 投資判断は必ず自己責任でお願いします。この記事は投資助言ではありません</small></p>
<p><small>📅 記事作成日：2025年1月2日</small></p>
"""
    
    # 文字数計算
    word_count = len(content.replace(' ', '').replace('\n', '').replace('<', '').replace('>', ''))
    
    article = {
        'title': title,
        'content': content,
        'word_count': word_count,
        'article_type': 'news_analysis',
        'category': 'ニュース解説',
        'tags': ['ビットコイン', '価格予想', 'スタンダードチャータード', '投資', '初心者向け'],
        'generation_date': now.isoformat(),
        'test_article': True
    }
    
    return article

def save_test_article(article):
    """テスト記事を保存"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"test_article_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        
        print(f"💾 テスト記事を保存しました: {filename}")
        return filename
    except Exception as e:
        print(f"❌ 記事保存エラー: {e}")
        return None

def main():
    """メイン実行"""
    print("🚀 テスト記事作成システム")
    print("=" * 80)
    
    print("✍️ 親しみやすい日本語でテスト記事を作成中...")
    
    # テスト記事生成
    article = create_test_article()
    
    # プレビュー表示
    print("\n" + "=" * 80)
    print("📝 生成されたテスト記事のプレビュー")
    print("=" * 80)
    print(f"タイトル: {article['title']}")
    print(f"文字数: {article['word_count']}字")
    print(f"カテゴリ: {article['category']}")
    print(f"タグ: {', '.join(article['tags'])}")
    print("\n--- 記事の冒頭 ---")
    print(article['content'][:800] + "...")
    print("=" * 80)
    
    # 保存
    saved_file = save_test_article(article)
    
    if saved_file:
        print("\n🎉 テスト記事の作成が完了しました！")
        print("\n📋 次のステップ:")
        print("1. 記事内容を確認")
        print("2. 必要に応じて編集")
        print("3. WordPressに投稿: python3 run_wordpress_publish.py")
        
        # 簡易HTMLプレビューファイルも作成
        html_preview = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }}
        h1 {{ color: #2c3e50; font-size: 28px; }}
        h2 {{ color: #34495e; font-size: 24px; margin-top: 30px; }}
        h3 {{ color: #7f8c8d; font-size: 20px; }}
        strong {{ color: #e74c3c; }}
        small {{ color: #95a5a6; }}
        hr {{ margin: 40px 0; border: none; border-top: 1px solid #ecf0f1; }}
        ul, ol {{ margin-left: 20px; }}
        li {{ margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>{article['title']}</h1>
    {article['content']}
</body>
</html>
"""
        
        preview_filename = f"test_article_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(preview_filename, 'w', encoding='utf-8') as f:
            f.write(html_preview)
        
        print(f"\n🌐 HTMLプレビューも作成しました: {preview_filename}")
        print("ブラウザで開いて記事の見た目を確認できます")

if __name__ == "__main__":
    main()