#!/usr/bin/env python3
"""
画像表示問題をデバッグして修正
"""

import logging
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.publishers.wordpress_client import WordPressClient

def setup_logging():
    """ログ設定"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def debug_and_fix_images():
    """画像表示問題を修正"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 設定とクライアントを初期化
        config = Config()
        wp_client = WordPressClient(config)
        
        # まず、アップロードした画像の情報を確認
        logger.info("アップロード済み画像の詳細を確認中...")
        
        # WordPressの最近のメディアを確認
        media_list = wp_client._make_request('GET', 'media?per_page=20&orderby=date&order=desc')
        
        if media_list:
            print("\n=== アップロード済みメディア一覧 ===")
            for i, media in enumerate(media_list[:10]):
                print(f"ID: {media['id']}")
                print(f"タイトル: {media['title']['rendered']}")
                print(f"URL: {media['source_url']}")
                print(f"サイズ: {media.get('media_details', {}).get('width', 'N/A')}x{media.get('media_details', {}).get('height', 'N/A')}")
                print(f"ファイル名: {media['media_details']['file'] if 'media_details' in media else 'N/A'}")
                print("---")
        
        # 正しい画像URLを使用して記事を再構築
        media_urls = {}
        if media_list:
            # 最近の9つのメディアを取得（ID順）
            recent_media = sorted(media_list[:9], key=lambda x: x['id'])
            
            for i, media in enumerate(recent_media):
                if i == 0:
                    media_urls['featured'] = {'id': media['id'], 'url': media['source_url']}
                else:
                    media_urls[f'section_{i}'] = {'id': media['id'], 'url': media['source_url']}
        
        print(f"\n使用する画像URL: {len(media_urls)}個")
        for key, value in media_urls.items():
            print(f"{key}: ID {value['id']} - {value['url']}")
        
        # 正しい画像URLを使って記事を再構築
        content = f"""
<h2>【速報】ビットコイン11.8万ドル突破の瞬間</h2>

<p>みなさん、こんにちは！</p>
<p>今日は本当に歴史的な日となりました。ビットコインが遂に11万8000ドル（約1187万円）の大台を突破し、史上最高値を更新したのです！</p>
<p>7月13日の取引で、ビットコインは一時118,872.85ドルまで上昇し、従来の最高値を大幅に上回りました。現在は117,955ドル付近で推移しており、24時間で約4%の上昇を記録しています。</p>
<p>この歴史的な瞬間は、仮想通貨業界にとって新たなマイルストーンとなり、多くの投資家や市場関係者が注目しています。</p>

<figure class="wp-block-image size-large aligncenter">
<img src="{media_urls.get('section_1', {}).get('url', '')}" alt="ビットコイン史上最高値突破" class="wp-image-{media_urls.get('section_1', {}).get('id', '')}"/>
<figcaption>図1: ビットコイン史上最高値突破</figcaption>
</figure>

<h2>ETF大量流入が史上最高値を後押し</h2>

<p>今回の価格急騰の最大の要因は、機関投資家によるETF（上場投資信託）への大量資金流入です。</p>

<p><strong>【木曜日の記録的な流入額】</strong><br>
• ビットコインETF: 11.8億ドル（2025年最大）<br>
• イーサリアムETF: 3.83億ドル（史上2番目）</p>

<p>特に注目すべきは、米国のスポットビットコインETFが2日連続で10億ドル超の流入を記録したことです。これは史上初の快挙であり、機関投資家の仮想通貨に対する信頼が劇的に向上していることを示しています。</p>

<p>ブラックロックのiShares Bitcoin ETFが流入の中心となっており、1日で3.7億ドルを記録しました。</p>

<figure class="wp-block-image size-large aligncenter">
<img src="{media_urls.get('section_2', {}).get('url', '')}" alt="ETF流入チャート" class="wp-image-{media_urls.get('section_2', {}).get('id', '')}"/>
<figcaption>図2: ETF大量流入データ</figcaption>
</figure>

<h2>市場への三段階影響分析</h2>

<p>この史上最高値更新は、短期・中期・長期にわたって市場に大きな影響を与えると予想されます。</p>

<p><strong>【短期影響（1-3ヶ月）】</strong><br>
• ビットコインは週間で約10%上昇、4月25日以来の最高成績<br>
• ショートポジションの大量強制決済：過去24時間で5.5億ドル<br>
• アルトコインへの波及効果：ETH、UNI、SEIなども新高値更新</p>

<p><strong>【中期影響（3-12ヶ月）】</strong><br>
• 機関投資家の参入加速<br>
• 他の仮想通貨ETF承認への期待感上昇<br>
• 規制環境の更なる整備</p>

<p><strong>【長期影響（1年以上）】</strong><br>
• 仮想通貨の資産クラスとしての地位確立<br>
• グローバルな決済インフラとしての普及<br>
• 中央銀行デジタル通貨（CBDC）開発の促進</p>

<figure class="wp-block-image size-large aligncenter">
<img src="{media_urls.get('section_3', {}).get('url', '')}" alt="市場影響分析図" class="wp-image-{media_urls.get('section_3', {}).get('id', '')}"/>
<figcaption>図3: 三段階市場影響分析</figcaption>
</figure>

<h2>専門家の見解：強気と慎重論</h2>

<p>市場の専門家たちは、今回の価格上昇について様々な見解を示しています。</p>

<p><strong>【強気派の意見】</strong><br>
Galaxy Digitalの研究責任者は「ビットコインは2025年中に18.5万ドルに達する可能性がある」と予測。スタンダードチャータード銀行も「年末までに20万ドル突破」とする強気の見通しを維持しています。</p>

<p><strong>【慎重派の意見】</strong><br>
一方で、一部のアナリストは「急激な上昇には調整が伴う可能性が高い」と警告。特に、レバレッジ取引の増加や市場の過熱感を懸念する声も上がっています。</p>

<p><strong>【バランス派の見解】</strong><br>
多くの機関投資家は「長期的なトレンドは上昇だが、短期的なボラティリティは覚悟すべき」として、堅実な投資戦略を推奨しています。</p>

<figure class="wp-block-image size-large aligncenter">
<img src="{media_urls.get('section_4', {}).get('url', '')}" alt="専門家見解" class="wp-image-{media_urls.get('section_4', {}).get('id', '')}"/>
<figcaption>図4: 専門家の多様な見解</figcaption>
</figure>

<h2>国際動向：世界各国の反応</h2>

<p>ビットコインの史上最高値更新は、世界各国で大きな注目を集めています。</p>

<p><strong>【アメリカの動向】</strong><br>
来週7月14日から始まる議会の「クリプト・ウィーク」が市場の追い風となっています。GENIUS法案やステーブルコイン規制枠組みの議論が、仮想通貨業界の法的地位を明確化する重要な機会となります。</p>

<p><strong>【ヨーロッパの動向】</strong><br>
欧州中央銀行（ECB）は仮想通貨の規制フレームワーク「MiCA」の実施を加速させており、機関投資家にとってより安全な投資環境が整いつつあります。</p>

<p><strong>【アジアの動向】</strong><br>
日本では金融庁が仮想通貨ETFの承認に向けた検討を本格化。韓国やシンガポールでも同様の動きが見られ、アジア太平洋地域での普及が期待されています。</p>

<figure class="wp-block-image size-large aligncenter">
<img src="{media_urls.get('section_5', {}).get('url', '')}" alt="国際動向" class="wp-image-{media_urls.get('section_5', {}).get('id', '')}"/>
<figcaption>図5: 世界各国の反応</figcaption>
</figure>

<h2>投資家向け具体的アドバイス</h2>

<p>この歴史的な価格上昇を受けて、投資家の皆さんにお伝えしたいアドバイスをまとめました。</p>

<p><strong>【初心者向けアクションプラン】</strong><br>
1. 小額から始める：まずは余剰資金の5-10%程度で<br>
2. 定期積立投資を検討：価格変動リスクを分散<br>
3. 信頼できる取引所を選択：セキュリティと規制対応を重視<br>
4. 情報収集を継続：市場動向と規制変化をウォッチ</p>

<p><strong>【経験者向けアクションプラン】</strong><br>
1. ポートフォリオの再バランス：利益確定とリスク管理<br>
2. ETF投資の検討：直接保有のリスクを軽減<br>
3. 税務対策の準備：キャピタルゲイン税の計算と申告<br>
4. ステーキングやDeFiの活用：追加収益機会の探索</p>

<p><strong>【共通の注意点】</strong><br>
• レバレッジ取引は避ける<br>
• 感情的な取引を控える<br>
• 長期視点を維持する</p>

<figure class="wp-block-image size-large aligncenter">
<img src="{media_urls.get('section_6', {}).get('url', '')}" alt="投資アドバイス" class="wp-image-{media_urls.get('section_6', {}).get('id', '')}"/>
<figcaption>図6: 投資家向けアドバイス</figcaption>
</figure>

<h2>よくある質問（Q&A）</h2>

<p><strong>【Q1: 今から買っても遅くないですか？】</strong><br>
A: 長期投資の観点では、まだ早期段階と考える専門家が多数います。ただし、短期的な調整の可能性もあるため、分散投資を心がけてください。</p>

<p><strong>【Q2: ビットコインETFと直接購入の違いは？】</strong><br>
A: ETFは証券会社で簡単に売買でき、税務処理も株式と同様です。直接購入は自己管理が必要ですが、より多くの投資機会があります。</p>

<p><strong>【Q3: 税金はどうなりますか？】</strong><br>
A: 日本では雑所得として総合課税の対象です。利益が出た場合は確定申告が必要になります。</p>

<p><strong>【Q4: 他の仮想通貨も買うべき？】</strong><br>
A: ビットコインが「デジタルゴールド」なら、イーサリアムは「デジタル石油」と言われます。用途や技術的特徴を理解した上で判断してください。</p>

<p><strong>【Q5: 暴落リスクはありませんか？】</strong><br>
A: 仮想通貨は高ボラティリティ資産です。過去にも大きな調整を経験しており、リスク管理は必須です。</p>

<figure class="wp-block-image size-large aligncenter">
<img src="{media_urls.get('section_7', {}).get('url', '')}" alt="Q&A" class="wp-image-{media_urls.get('section_7', {}).get('id', '')}"/>
<figcaption>図7: よくある質問</figcaption>
</figure>

<h2>まとめ：新時代の始まり</h2>

<p>ビットコインの11.8万ドル突破は、単なる価格更新以上の意味を持っています。</p>

<p><strong>【重要ポイントの整理】</strong><br>
1. 機関投資家の本格参入が価格上昇を支えている<br>
2. 規制環境の整備が投資家の信頼を高めている<br>
3. ETFという新しい投資手段が普及を加速させている<br>
4. 世界各国で仮想通貨の法的地位が明確化されつつある</p>

<p><strong>【今後の展望】</strong><br>
• 年末までに20万ドル到達の可能性<br>
• 他の仮想通貨ETF承認による市場拡大<br>
• デジタル資産の主流金融商品化</p>

<p>この歴史的な瞬間を目撃している私たちは、金融史の転換点に立っています。ビットコインが示す新しい価値保存手段としての可能性は、今後も多くの投資家に選択肢を提供し続けるでしょう。</p>

<p>投資は自己責任ですが、正しい知識と適切なリスク管理があれば、この新時代の恩恵を受けることができます。引き続き市場動向に注目し、賢明な判断を心がけていきましょう。</p>

<p><strong>【重要な免責事項】</strong><br>
本記事は情報提供を目的としており、投資助言ではありません。仮想通貨投資にはリスクが伴いますので、投資判断は自己責任でお願いします。</p>

<figure class="wp-block-image size-large aligncenter">
<img src="{media_urls.get('section_8', {}).get('url', '')}" alt="まとめ" class="wp-image-{media_urls.get('section_8', {}).get('id', '')}"/>
<figcaption>図8: 新時代の始まり</figcaption>
</figure>

"""

        # 記事データを作成
        article_data = {
            'title': '【速報】ビットコイン史上最高値11.8万ドル突破｜機関投資ETF流入が支える大相場',
            'content': content,
            'featured_media': media_urls.get('featured', {}).get('id')  # アイキャッチ画像
        }
        
        logger.info("正しい画像URLで記事を更新中...")
        
        # 記事を更新（ID: 883）
        result = wp_client.update_article(883, article_data)
        
        if result and result.get('success'):
            print("\n✅ 画像表示修正完了!")
            print(f"📝 投稿ID: {result.get('id')}")
            print(f"🌐 URL: {result.get('url')}")
            print(f"🎨 画像: {len(media_urls)}枚の実際の画像URLを使用")
            print("\n記事をリロードして画像表示を確認してください！")
            
        else:
            print("❌ 記事更新に失敗しました")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        logger.error(f"修正エラー: {e}")

if __name__ == "__main__":
    debug_and_fix_images()