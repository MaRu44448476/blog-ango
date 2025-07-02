#!/usr/bin/env python3
"""
選択された候補で記事を生成
"""

import json
import sys
import glob
import os
from datetime import datetime

def load_latest_candidates():
    """最新の候補データを読み込み"""
    candidate_files = glob.glob("article_candidates_*.json")
    
    if not candidate_files:
        print("❌ 候補データが見つかりません")
        print("まず show_article_candidates.py を実行してください")
        return None
    
    latest_file = max(candidate_files, key=os.path.getctime)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"📄 候補データを読み込みました: {latest_file}")
        return data['candidates']
    except Exception as e:
        print(f"❌ 候補データ読み込みエラー: {e}")
        return None

def generate_article_from_candidate(candidate):
    """選択された候補から記事を生成"""
    news_item = candidate['news']
    japanese_title = candidate['japanese_title']
    categories = candidate['categories']
    angles = candidate['angles']
    
    now = datetime.now()
    
    # 記事タイトルを生成（候補の切り口を参考に）
    if angles:
        # 最初の切り口からタイトルを生成
        main_angle = angles[0]
        if "価格上昇" in main_angle:
            title = f"【急上昇】{japanese_title}｜価格上昇の背景を初心者向けに解説！"
        elif "価格下落" in main_angle:
            title = f"【要注意】{japanese_title}｜下落の原因と今後の見通しは？"
        elif "規制" in main_angle:
            title = f"【解説】{japanese_title}｜日本の投資家への影響は？"
        elif "機関投資家" in main_angle:
            title = f"【話題】{japanese_title}｜大手参入で何が変わる？"
        elif "技術" in main_angle or "DeFi" in main_angle:
            title = f"【最新技術】{japanese_title}｜仕組みをわかりやすく解説"
        else:
            title = f"【注目】{japanese_title}｜今知っておくべき理由とは？"
    else:
        title = f"【解説】{japanese_title}｜初心者にもわかりやすく説明します"
    
    # 記事本文を生成
    content = generate_article_content(news_item, japanese_title, categories, angles)
    
    # タグを生成
    tags = generate_tags_from_categories(categories)
    tags.extend(['仮想通貨', '初心者向け', 'わかりやすい解説'])
    
    # カテゴリを決定
    category = determine_main_category(categories)
    
    # 文字数計算
    word_count = len(content.replace(' ', '').replace('\n', '').replace('<', '').replace('>', ''))
    
    # SEO関連データを生成
    seo_data = generate_seo_data(title, japanese_title, categories, tags)
    
    article = {
        'title': title,
        'content': content,
        'word_count': word_count,
        'target_word_count': 4000,  # 目標文字数
        'article_type': 'news_friendly_long',
        'category': category,
        'tags': list(set(tags)),  # 重複削除
        'meta_description': seo_data['meta_description'],
        'meta_keywords': seo_data['meta_keywords'],
        'focus_keyword': seo_data['focus_keyword'],
        'seo_title': seo_data['seo_title'],
        'excerpt': seo_data['excerpt'],
        'generation_date': now.isoformat(),
        'original_title': news_item['title'],
        'japanese_title': japanese_title,
        'original_source': news_item['source'],
        'original_url': news_item['url'],
        'importance_score': news_item.get('importance_score', 0),
        'interest_score': candidate.get('interest_score', 0),
        'selected_angle': angles[0] if angles else None,
        'news_categories': categories
    }
    
    return article

def generate_article_content(news_item, japanese_title, categories, angles):
    """記事の本文を生成（4000字版）"""
    
    content = f"""
<h2>今回のニュースをざっくり説明すると...</h2>
<p>みなさん、こんにちは！今日は仮想通貨界隈で<strong>超大きな話題</strong>になっているニュースについて、できるだけわかりやすく解説していきたいと思います。</p>

<p>今回取り上げるのは、「<strong>{japanese_title}</strong>」というニュースです。{news_item['source']}から報じられたこの情報、正直言って<strong>とんでもなく重要</strong>な内容なんです！</p>

<p>「えっ、何がそんなにすごいの？」と思った方、大正解です。このニュースが仮想通貨業界、そして私たち個人投資家にどんな影響を与えるのか、一緒に詳しく見ていきましょう！</p>
"""
    
    # カテゴリに応じた詳細導入
    if '💰 価格・相場' in categories:
        content += """
<p>このニュースは<strong>価格に直接影響する可能性がある</strong>超重要な情報です。投資をされている方は絶対に見逃せませんよ！</p>
<p>特に最近の仮想通貨市場は、こういった大きなニュースに敏感に反応する傾向があります。過去の事例を見ても、同様のニュースが発表された時は市場が大きく動きました。</p>
"""
    elif '⚖️ 規制・政策' in categories:
        content += """
<p>このニュースは<strong>規制や政策に関わる超重要な内容</strong>で、長期的に仮想通貨市場に大きな影響を与える可能性があります。</p>
<p>規制ニュースって聞くと「難しそう...」と思うかもしれませんが、実は私たちの投資活動に直結する大切な情報なんです。しっかりと理解しておけば、他の投資家より一歩先を行けますよ！</p>
"""
    elif '🏦 機関投資' in categories:
        content += """
<p>このニュースは<strong>機関投資家の動向</strong>に関する超注目の情報で、市場の流れを読む上で重要な手がかりになりそうです。</p>
<p>「機関投資家って何？」という方もいるかもしれませんね。簡単に言うと、銀行や保険会社、投資ファンドなど、大きなお金を動かす投資のプロたちのことです。彼らの動きは市場に大きな影響を与えるんです。</p>
"""
    elif '🔗 DeFi・プロトコル' in categories:
        content += """
<p>このニュースは<strong>DeFi（分散型金融）</strong>に関する最新情報で、仮想通貨の技術的な進歩を知る上で興味深い内容です。</p>
"""
    
    content += f"""
<h2>具体的にはどんな内容なの？詳しく解説します</h2>
<p>元のニュースを詳しく読み解いてみると、以下のような重要なポイントが見えてきます：</p>

<blockquote>
<p>{news_item.get('description', '詳細な情報が提供されています')[:300]}...</p>
</blockquote>

<p>「なるほど、でもこれって具体的に何を意味するの？普通の言葉で説明してよ！」と思った方も多いのではないでしょうか。大丈夫です、一つずつ丁寧に解説していきますね！</p>

<h3>このニュースの背景を理解しよう</h3>
<p>まず、なぜこのニュースが今このタイミングで発表されたのか、その背景から説明しましょう。</p>

<p>実は、仮想通貨業界では最近、<strong>大きな変化の波</strong>が押し寄せています。特に以下のような動きが活発になっているんです：</p>

<ul>
<li>機関投資家の参入が加速している</li>
<li>規制環境が整備されつつある</li>
<li>一般投資家の関心が高まっている</li>
<li>技術的な進歩が続いている</li>
</ul>

<p>こうした流れの中で、今回のニュースが発表されたというわけです。つまり、<strong>偶然ではなく必然</strong>と言えるかもしれませんね。</p>
"""
    
    # カテゴリ別の詳細解説
    if '💰 価格・相場' in categories:
        content += generate_price_analysis_section(news_item, japanese_title)
    elif '⚖️ 規制・政策' in categories:
        content += generate_regulation_analysis_section(news_item, japanese_title)
    elif '🏦 機関投資' in categories:
        content += generate_institutional_analysis_section(news_item, japanese_title)
    elif '🔗 DeFi・プロトコル' in categories:
        content += generate_defi_analysis_section(news_item, japanese_title)
    else:
        content += generate_general_analysis_section(news_item, japanese_title)
    
    # 共通のセクション（4000字対応版）
    content += f"""
<h2>私たちへの影響は？詳しく分析してみよう</h2>
<p>このニュースが私たち個人投資家にとってどんな意味を持つのか、短期・中期・長期の視点で詳しく考えてみましょう。</p>

<h3>📅 短期的な影響（今後1-3ヶ月）</h3>
<p>まず短期的には、<strong>市場の雰囲気や投資家心理</strong>に影響を与える可能性があります。</p>

<ul>
<li><strong>価格の変動</strong>：ニュースが好材料として受け取られれば上昇、悪材料なら下落の可能性</li>
<li><strong>取引量の増加</strong>：注目度が高まることで売買が活発になる</li>
<li><strong>他の銘柄への影響</strong>：関連する仮想通貨にも波及効果がある場合も</li>
</ul>

<p>ただし、短期的な変動に一喜一憂する必要はありません。むしろ、<strong>冷静に情報を分析</strong>することが大切です。</p>

<h3>📊 中期的な影響（今後3-12ヶ月）</h3>
<p>中期的には、より本質的な変化が現れてくる可能性があります。</p>

<ul>
<li><strong>業界の構造変化</strong>：新しいルールや技術の普及により、業界全体が変わる</li>
<li><strong>投資家層の拡大</strong>：機関投資家や一般投資家の参入が進む</li>
<li><strong>新しいサービスの登場</strong>：このニュースを受けて新たなビジネスが生まれる</li>
</ul>

<h3>🔮 長期的な影響（1年以上）</h3>
<p>長期的には、仮想通貨業界の<strong>根本的な方向性</strong>を左右する可能性があります。</p>

<p>過去の事例を見ても、こうした重要なニュースは後から振り返ると「あの時が転換点だった」と言われることが多いんです。今回のニュースも、そうした歴史的な意味を持つかもしれませんね。</p>

<h2>専門家はどう見ている？業界の反応をチェック</h2>
<p>このニュースに対して、業界の専門家や有識者はどのような反応を示しているのでしょうか？</p>

<h3>🎯 ポジティブな意見</h3>
<ul>
<li>「業界の健全な発展に寄与する」</li>
<li>「長期的には投資家にとってプラス」</li>
<li>「技術革新が加速する可能性」</li>
</ul>

<h3>⚠️ 慎重な意見</h3>
<ul>
<li>「短期的には混乱が生じる可能性」</li>
<li>「規制の詳細を見極める必要がある」</li>
<li>「市場の成熟度を見極めることが重要」</li>
</ul>

<h2>他の国ではどうなっている？国際的な動向</h2>
<p>実は、このようなニュースは日本だけでなく、世界各国で同様の動きが見られています。</p>

<h3>🌍 アメリカの動向</h3>
<p>アメリカでは先進的な取り組みが多く、今回のようなニュースに対しても積極的な姿勢を見せています。</p>

<h3>🇪🇺 ヨーロッパの動向</h3>
<p>ヨーロッパでは規制を重視しつつも、イノベーションを促進するバランスの取れたアプローチを取っています。</p>

<h3>🌏 アジアの動向</h3>
<p>アジア各国でも、それぞれの国情に合わせた対応を検討している状況です。</p>

<h2>で、結局どうすればいいの？具体的なアクションプラン</h2>
<p>このニュースを受けて、私たちはどう行動すればいいのでしょうか？段階別に具体的なアドバイスをお伝えします。</p>

<h3>🔰 初心者の方へ</h3>
<p><strong>まず大切なのは、慌てないこと</strong>です。一つのニュースで大きな投資判断をするのはリスクが高すぎます。</p>

<ol>
<li><strong>情報収集を続ける</strong>：複数のソースから情報を得る</li>
<li><strong>基礎知識を身につける</strong>：仮想通貨の仕組みを理解する</li>
<li><strong>少額から始める</strong>：いきなり大金を投じない</li>
<li><strong>長期的な視点を持つ</strong>：短期の値動きに一喜一憂しない</li>
</ol>

<h3>💼 経験者の方へ</h3>
<p>すでに仮想通貨投資の経験がある方は、以下の点を検討してみてください：</p>

<ol>
<li><strong>ポートフォリオの見直し</strong>：今回のニュースを受けてバランスを調整</li>
<li><strong>リスク管理の徹底</strong>：想定外の事態に備える</li>
<li><strong>新しい機会の探索</strong>：このニュースが生み出す投資機会を見極める</li>
<li><strong>継続的な学習</strong>：変化する業界についていくための勉強</li>
</ol>

<h2>よくある質問にお答えします！</h2>

<h3>Q: このニュースで価格は上がりますか？</h3>
<p>A: 価格の予想は非常に難しく、様々な要因に左右されます。大切なのは、短期的な値動きではなく、長期的な価値を見極めることです。</p>

<h3>Q: 今から投資を始めても遅くないですか？</h3>
<p>A: 仮想通貨はまだ発展途上の分野です。適切な知識とリスク管理があれば、いつ始めても学ぶことは多いでしょう。</p>

<h3>Q: どの通貨に投資すればいいですか？</h3>
<p>A: 投資判断は個人の責任で行うものです。まずは主要な通貨（ビットコイン、イーサリアムなど）について学ぶことをおすすめします。</p>

<h2>まとめ：今後の展開に注目しよう</h2>
<p>今回は「{japanese_title}」というビッグニュースについて、様々な角度から詳しく解説してきました。</p>

<p>このニュースの重要なポイントをもう一度整理すると：</p>

<ul>
<li>業界全体に大きな影響を与える可能性がある</li>
<li>短期・中期・長期でそれぞれ異なる影響が予想される</li>
<li>専門家の間でも意見が分かれている</li>
<li>国際的な動向も注視する必要がある</li>
<li>投資判断は慎重に、リスク管理を徹底して行うべき</li>
</ul>

<p>仮想通貨の世界は日々新しい情報が飛び交っていて、すべてを追いかけるのは大変かもしれません。でも、こうして一つ一つのニュースを深く理解していくことで、この業界の流れが少しずつ見えてくるはずです。</p>

<p><strong>大切なのは、情報に振り回されることなく、自分なりの投資スタイルを確立すること</strong>。そして、常に学び続ける姿勢を持つことです。</p>

<p>これからも、皆さんにとって役立つ情報をわかりやすく、そして詳しくお届けしていきたいと思います。今回のような重要なニュースが出た時は、ぜひまたこのサイトをチェックしてくださいね！</p>

<p>最後まで読んでいただき、本当にありがとうございました。皆さんの仮想通貨投資が成功することを心から願っています！</p>

<hr>
<p><small>📌 元記事: <a href="{news_item['url']}" target="_blank" rel="noopener">{news_item['source']}</a></small></p>
<p><small>⚠️ この記事は情報提供を目的としており、投資助言ではありません。投資判断は自己責任でお願いします。</small></p>
<p><small>📅 記事作成日: {datetime.now().strftime('%Y年%m月%d日')}</small></p>
<p><small>🏷️ 関連タグ: 仮想通貨ニュース、投資情報、初心者向け解説</small></p>
"""
    
    return content

def generate_price_analysis_section(news_item, japanese_title):
    """価格分析セクション"""
    return """
<h2>価格への影響を考えてみよう</h2>
<p>このニュースが仮想通貨の価格にどんな影響を与える可能性があるのか、考えてみましょう。</p>

<h3>プラス要因として考えられること</h3>
<ul>
<li>市場の注目度アップ</li>
<li>新規投資家の参入</li>
<li>機関投資家の関心増</li>
</ul>

<h3>注意すべきリスク</h3>
<ul>
<li>短期的な値動きの激しさ</li>
<li>予想と異なる結果の可能性</li>
<li>他の要因による影響</li>
</ul>

<p>「じゃあ今すぐ買った方がいいの？」と思うかもしれませんが、<strong>投資はタイミングが全て</strong>ではありません。しっかりと情報を集めて、冷静に判断することが大切です。</p>
"""

def generate_regulation_analysis_section(news_item, japanese_title):
    """規制分析セクション"""
    return """
<h2>規制ニュースの読み方</h2>
<p>規制に関するニュースは、一見難しそうに見えますが、実は私たちの投資活動に直結する重要な情報です。</p>

<h3>規制がもたらすもの</h3>
<ul>
<li><strong>透明性の向上</strong>: ルールが明確になることで、安心して投資できる</li>
<li><strong>市場の安定化</strong>: 悪質な業者が排除され、健全な市場になる</li>
<li><strong>機関投資家の参入</strong>: 法的な枠組みができることで、大手も参加しやすくなる</li>
</ul>

<h3>一方で注意すべき点</h3>
<ul>
<li>規制の内容によっては取引が制限される可能性</li>
<li>コンプライアンスコストの増加</li>
<li>短期的には市場が不安定になることも</li>
</ul>

<p>規制ニュースは<strong>長期的な視点</strong>で捉えることが重要です。一時的に価格が下がったとしても、健全な市場の発展につながるなら、それは良いニュースと言えるでしょう。</p>
"""

def generate_institutional_analysis_section(news_item, japanese_title):
    """機関投資分析セクション"""
    return """
<h2>大手の動きが意味すること</h2>
<p>機関投資家や大手企業の動向は、仮想通貨市場の今後を占う重要な指標です。</p>

<h3>機関投資家参入のメリット</h3>
<ul>
<li><strong>市場規模の拡大</strong>: 大きな資金が流入することで市場が成長</li>
<li><strong>価格の安定化</strong>: 長期保有により、価格変動が緩やかになる傾向</li>
<li><strong>信頼性の向上</strong>: 大手の参入により、一般投資家の信頼も向上</li>
</ul>

<h3>個人投資家への影響</h3>
<p>「大手が入ってくると、個人投資家は不利になるんじゃない？」と心配する声もありますが、必ずしもそうではありません。</p>

<ul>
<li>市場全体の成長により、保有資産の価値も上昇する可能性</li>
<li>より多くの投資商品やサービスが提供される</li>
<li>規制整備が進み、安全な投資環境が整う</li>
</ul>

<p>重要なのは、<strong>機関投資家と同じ方向を向く</strong>こと。彼らの投資戦略や考え方を参考にして、自分なりの投資スタイルを確立していきましょう。</p>
"""

def generate_defi_analysis_section(news_item, japanese_title):
    """DeFi分析セクション"""
    return """
<h2>DeFiの世界をのぞいてみよう</h2>
<p>DeFi（分散型金融）と聞くと、「難しそう...」と思うかもしれませんが、実は私たちの生活に身近な存在になりつつあります。</p>

<h3>DeFiって何がすごいの？</h3>
<ul>
<li><strong>銀行を通さない金融サービス</strong>: 24時間いつでも利用可能</li>
<li><strong>透明性</strong>: すべての取引がブロックチェーン上で公開</li>
<li><strong>グローバル</strong>: 世界中の誰でも同じサービスを利用可能</li>
</ul>

<h3>初心者が知っておくべきポイント</h3>
<ul>
<li>従来の銀行サービスより高い利回りが期待できることがある</li>
<li>ただし、リスクも従来より高い場合が多い</li>
<li>技術的な理解がある程度必要</li>
</ul>

<p>DeFiは仮想通貨の<strong>実用性を示す重要な分野</strong>です。今回のニュースのような技術的な進歩が、将来的にはもっと使いやすいサービスとして私たちの生活に入ってくるかもしれませんね。</p>
"""

def generate_general_analysis_section(news_item, japanese_title):
    """一般的な分析セクション"""
    return """
<h2>このニュースの重要性</h2>
<p>一見すると「へぇ〜」で終わってしまいそうなニュースでも、実は仮想通貨業界の大きなトレンドを示している場合があります。</p>

<h3>なぜ注目すべきなのか</h3>
<ul>
<li>業界全体の方向性がわかる</li>
<li>新しい技術やサービスの可能性が見える</li>
<li>将来の投資機会のヒントになる</li>
</ul>

<h3>情報収集のコツ</h3>
<p>仮想通貨の世界では、小さなニュースが後に大きな変化につながることがよくあります。</p>

<ul>
<li>複数のニュースソースをチェック</li>
<li>海外の動向にも注目</li>
<li>技術的な進歩にアンテナを張る</li>
</ul>
"""

def generate_tags_from_categories(categories):
    """カテゴリからタグを生成"""
    tag_mapping = {
        '💰 価格・相場': ['価格分析', '相場', '投資'],
        '⚖️ 規制・政策': ['規制', '政策', '法律'],
        '🏦 機関投資': ['機関投資家', '企業', '投資'],
        '🔗 DeFi・プロトコル': ['DeFi', 'プロトコル', '技術'],
        '🎨 NFT・ゲーム': ['NFT', 'ゲーム', 'アート'],
        '🏢 取引所・プラットフォーム': ['取引所', 'プラットフォーム'],
        '🤝 企業・提携': ['企業', '提携', 'パートナーシップ'],
        '⚙️ 技術・開発': ['技術', '開発', 'アップデート'],
        '🔐 セキュリティ': ['セキュリティ', 'ハッキング', '安全性'],
        '📊 マクロ経済': ['経済', 'マクロ', '金融政策']
    }
    
    tags = []
    for category in categories:
        if category in tag_mapping:
            tags.extend(tag_mapping[category])
    
    return tags

def determine_main_category(categories):
    """メインカテゴリを決定"""
    category_mapping = {
        '💰 価格・相場': '市場分析',
        '⚖️ 規制・政策': '規制・政策',
        '🏦 機関投資': '投資',
        '🔗 DeFi・プロトコル': 'DeFi',
        '🎨 NFT・ゲーム': 'NFT',
        '🏢 取引所・プラットフォーム': '取引所',
        '🤝 企業・提携': '企業ニュース',
        '⚙️ 技術・開発': '技術',
        '🔐 セキュリティ': 'セキュリティ',
        '📊 マクロ経済': '経済'
    }
    
    if categories:
        return category_mapping.get(categories[0], 'ニュース解説')
    return 'ニュース解説'

def save_article(article):
    """記事をJSONファイルに保存"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"selected_article_{timestamp}.json"
    
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
    if len(sys.argv) != 2:
        print("使用方法: python3 run_selected_article_generator.py [候補番号]")
        print("例: python3 run_selected_article_generator.py 1")
        return
    
    try:
        selected_index = int(sys.argv[1])
    except ValueError:
        print("❌ 候補番号は数字で入力してください")
        return
    
    print(f"🚀 候補 {selected_index} の記事を生成します")
    print("=" * 80)
    
    # 候補データを読み込み
    candidates = load_latest_candidates()
    if not candidates:
        return
    
    # 選択された候補を確認
    if selected_index < 1 or selected_index > len(candidates):
        print(f"❌ 無効な候補番号です。1-{len(candidates)} の範囲で入力してください")
        return
    
    selected_candidate = candidates[selected_index - 1]
    
    print(f"✅ 選択された記事: {selected_candidate['japanese_title']}")
    print(f"📊 重要度: {selected_candidate['news']['importance_score']:.1f}/100")
    print(f"👥 読者興味度: {selected_candidate['interest_score']:.1f}/100")
    print("✍️ 記事を生成中...")
    
    # 記事生成
    article = generate_article_from_candidate(selected_candidate)
    
    # プレビュー表示（SEO情報付き）
    print("\n" + "=" * 80)
    print("📝 生成された記事のプレビュー")
    print("=" * 80)
    print(f"タイトル: {article['title']}")
    print(f"SEOタイトル: {article['seo_title']}")
    print(f"文字数: {article['word_count']}字 (目標: {article['target_word_count']}字)")
    print(f"カテゴリ: {article['category']}")
    print(f"メインキーワード: {article['focus_keyword']}")
    print(f"タグ: {', '.join(article['tags'])}")
    print(f"メタキーワード: {', '.join(article['meta_keywords'])}")
    print(f"選択された切り口: {article.get('selected_angle', 'なし')}")
    print(f"\nメタ説明文:")
    print(f"{article['meta_description']}")
    print(f"\n抜粋:")
    print(f"{article['excerpt']}")
    print("\n--- 記事の冒頭 ---")
    print(article['content'][:500] + "...")
    print("=" * 80)
    
    # 保存
    save_article(article)
    
    print("\n🎉 記事生成が完了しました！")
    print("次のステップ: python3 run_wordpress_publish.py で投稿できます")

def generate_seo_data(title, japanese_title, categories, tags):
    """SEO関連データを生成"""
    
    # フォーカスキーワードを抽出
    focus_keywords = []
    if 'bitcoin' in japanese_title.lower() or 'ビットコイン' in japanese_title:
        focus_keywords.append('ビットコイン')
    if 'ethereum' in japanese_title.lower() or 'イーサリアム' in japanese_title:
        focus_keywords.append('イーサリアム')
    if 'etf' in japanese_title.lower():
        focus_keywords.append('ETF')
    if 'sec' in japanese_title.lower():
        focus_keywords.append('SEC')
    if 'grayscale' in japanese_title.lower():
        focus_keywords.append('Grayscale')
    
    primary_focus = focus_keywords[0] if focus_keywords else '仮想通貨'
    
    # メタディスクリプション生成（150-160文字）
    meta_description = f"{primary_focus}に関する最新ニュースを初心者にもわかりやすく解説。投資への影響、専門家の意見、今後の展望まで詳しく分析します。仮想通貨投資の判断材料として必見の内容です。"
    
    # メタキーワード生成
    meta_keywords = [
        primary_focus,
        '仮想通貨',
        '暗号資産',
        '投資',
        'ニュース解説',
        '初心者向け',
        '価格分析',
        '市場動向'
    ]
    
    # カテゴリから追加キーワード
    for category in categories:
        if '価格・相場' in category:
            meta_keywords.extend(['価格予想', '相場分析', 'チャート'])
        elif '規制・政策' in category:
            meta_keywords.extend(['規制', '政策', '法律'])
        elif '機関投資' in category:
            meta_keywords.extend(['機関投資家', '企業投資', '大口投資'])
    
    # SEOタイトル生成（32文字以内）
    seo_title = title
    if len(seo_title) > 32:
        # タイトルが長すぎる場合は短縮
        seo_title = f"【解説】{primary_focus}最新ニュース｜投資への影響は？"
    
    # 抜粋文生成
    excerpt = f"{primary_focus}に関する重要なニュースが発表されました。このニュースが仮想通貨市場や個人投資家に与える影響について、専門的な分析と初心者にもわかりやすい解説をお届けします。"
    
    return {
        'meta_description': meta_description,
        'meta_keywords': list(set(meta_keywords))[:10],  # 重複削除して上位10個
        'focus_keyword': primary_focus,
        'seo_title': seo_title,
        'excerpt': excerpt
    }

if __name__ == "__main__":
    main()