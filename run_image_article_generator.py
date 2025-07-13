#!/usr/bin/env python3
"""
画像付き記事生成スクリプト
ビットコイン史上最高値更新記事を画像付きで生成
"""

import logging
import sys
import os
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.config import Config
from src.generators.image_generator import ImageGenerator
from src.publishers.wordpress_client import WordPressClient

def setup_logging():
    """ログ設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/image_article.log'),
            logging.StreamHandler()
        ]
    )

def create_bitcoin_ath_article():
    """ビットコイン史上最高値更新記事を作成"""
    
    # 記事の基本情報
    article_data = {
        'title': '【速報】ビットコイン史上最高値11.8万ドル突破｜機関投資ETF流入が支える大相場',
        'article_type': 'breaking_news',
        'category': 'ビットコイン',
        'tags': ['ビットコイン', 'BTC', '史上最高値', 'ETF', '機関投資', '仮想通貨'],
        'importance_score': 98.0,
        'generation_date': datetime.now()
    }
    
    # 記事のセクション構成
    sections = [
        {
            'title': '【速報】ビットコイン11.8万ドル突破の瞬間',
            'content': '''みなさん、こんにちは！
            
今日は本当に歴史的な日となりました。ビットコインが遂に11万8000ドル（約1187万円）の大台を突破し、史上最高値を更新したのです！

7月13日の取引で、ビットコインは一時118,872.85ドルまで上昇し、従来の最高値を大幅に上回りました。現在は117,955ドル付近で推移しており、24時間で約4%の上昇を記録しています。

この歴史的な瞬間は、仮想通貨業界にとって新たなマイルストーンとなり、多くの投資家や市場関係者が注目しています。'''
        },
        {
            'title': 'ETF大量流入が史上最高値を後押し',
            'content': '''今回の価格急騰の最大の要因は、機関投資家によるETF（上場投資信託）への大量資金流入です。

【木曜日の記録的な流入額】
- ビットコインETF: 11.8億ドル（2025年最大）
- イーサリアムETF: 3.83億ドル（史上2番目）

特に注目すべきは、米国のスポットビットコインETFが2日連続で10億ドル超の流入を記録したことです。これは史上初の快挙であり、機関投資家の仮想通貨に対する信頼が劇的に向上していることを示しています。

ブラックロックのiShares Bitcoin ETFが流入の中心となっており、1日で3.7億ドルを記録しました。'''
        },
        {
            'title': '市場への三段階影響分析',
            'content': '''この史上最高値更新は、短期・中期・長期にわたって市場に大きな影響を与えると予想されます。

【短期影響（1-3ヶ月）】
- ビットコインは週間で約10%上昇、4月25日以来の最高成績
- ショートポジションの大量強制決済：過去24時間で5.5億ドル
- アルトコインへの波及効果：ETH、UNI、SEIなども新高値更新

【中期影響（3-12ヶ月）】
- 機関投資家の参入加速
- 他の仮想通貨ETF承認への期待感上昇
- 規制環境の更なる整備

【長期影響（1年以上）】
- 仮想通貨の資産クラスとしての地位確立
- グローバルな決済インフラとしての普及
- 中央銀行デジタル通貨（CBDC）開発の促進'''
        },
        {
            'title': '専門家の見解：強気と慎重論',
            'content': '''市場の専門家たちは、今回の価格上昇について様々な見解を示しています。

【強気派の意見】
Galaxy Digitalの研究責任者は「ビットコインは2025年中に18.5万ドルに達する可能性がある」と予測。スタンダードチャータード銀行も「年末までに20万ドル突破」とする強気の見通しを維持しています。

【慎重派の意見】
一方で、一部のアナリストは「急激な上昇には調整が伴う可能性が高い」と警告。特に、レバレッジ取引の増加や市場の過熱感を懸念する声も上がっています。

【バランス派の見解】
多くの機関投資家は「長期的なトレンドは上昇だが、短期的なボラティリティは覚悟すべき」として、堅実な投資戦略を推奨しています。'''
        },
        {
            'title': '国際動向：世界各国の反応',
            'content': '''ビットコインの史上最高値更新は、世界各国で大きな注目を集めています。

【アメリカの動向】
来週7月14日から始まる議会の「クリプト・ウィーク」が市場の追い風となっています。GENIUS法案やステーブルコイン規制枠組みの議論が、仮想通貨業界の法的地位を明確化する重要な機会となります。

【ヨーロッパの動向】
欧州中央銀行（ECB）は仮想通貨の規制フレームワーク「MiCA」の実施を加速させており、機関投資家にとってより安全な投資環境が整いつつあります。

【アジアの動向】
日本では金融庁が仮想通貨ETFの承認に向けた検討を本格化。韓国やシンガポールでも同様の動きが見られ、アジア太平洋地域での普及が期待されています。'''
        },
        {
            'title': '投資家向け具体的アドバイス',
            'content': '''この歴史的な価格上昇を受けて、投資家の皆さんにお伝えしたいアドバイスをまとめました。

【初心者向けアクションプラン】
1. 小額から始める：まずは余剰資金の5-10%程度で
2. 定期積立投資を検討：価格変動リスクを分散
3. 信頼できる取引所を選択：セキュリティと規制対応を重視
4. 情報収集を継続：市場動向と規制変化をウォッチ

【経験者向けアクションプラン】
1. ポートフォリオの再バランス：利益確定とリスク管理
2. ETF投資の検討：直接保有のリスクを軽減
3. 税務対策の準備：キャピタルゲイン税の計算と申告
4. ステーキングやDeFiの活用：追加収益機会の探索

【共通の注意点】
- レバレッジ取引は避ける
- 感情的な取引を控える
- 長期視点を維持する'''
        },
        {
            'title': 'よくある質問（Q&A）',
            'content': '''読者の皆さんから寄せられる代表的な質問にお答えします。

【Q1: 今から買っても遅くないですか？】
A: 長期投資の観点では、まだ早期段階と考える専門家が多数います。ただし、短期的な調整の可能性もあるため、分散投資を心がけてください。

【Q2: ビットコインETFと直接購入の違いは？】
A: ETFは証券会社で簡単に売買でき、税務処理も株式と同様です。直接購入は自己管理が必要ですが、より多くの投資機会があります。

【Q3: 税金はどうなりますか？】
A: 日本では雑所得として総合課税の対象です。利益が出た場合は確定申告が必要になります。

【Q4: 他の仮想通貨も買うべき？】
A: ビットコインが「デジタルゴールド」なら、イーサリアムは「デジタル石油」と言われます。用途や技術的特徴を理解した上で判断してください。

【Q5: 暴落リスクはありませんか？】
A: 仮想通貨は高ボラティリティ資産です。過去にも大きな調整を経験しており、リスク管理は必須です。'''
        },
        {
            'title': 'まとめ：新時代の始まり',
            'content': '''ビットコインの11.8万ドル突破は、単なる価格更新以上の意味を持っています。

【重要ポイントの整理】
1. 機関投資家の本格参入が価格上昇を支えている
2. 規制環境の整備が投資家の信頼を高めている
3. ETFという新しい投資手段が普及を加速させている
4. 世界各国で仮想通貨の法的地位が明確化されつつある

【今後の展望】
- 年末までに20万ドル到達の可能性
- 他の仮想通貨ETF承認による市場拡大
- デジタル資産の主流金融商品化

この歴史的な瞬間を目撃している私たちは、金融史の転換点に立っています。ビットコインが示す新しい価値保存手段としての可能性は、今後も多くの投資家に選択肢を提供し続けるでしょう。

投資は自己責任ですが、正しい知識と適切なリスク管理があれば、この新時代の恩恵を受けることができます。引き続き市場動向に注目し、賢明な判断を心がけていきましょう。

【重要な免責事項】
本記事は情報提供を目的としており、投資助言ではありません。仮想通貨投資にはリスクが伴いますので、投資判断は自己責任でお願いします。'''
        }
    ]
    
    return article_data, sections

def generate_article_with_images():
    """画像付き記事を生成"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("画像付きビットコイン記事生成を開始")
    
    try:
        # 設定とクライアントを初期化
        config = Config()
        if not config.validate_config():
            logger.error("設定の検証に失敗しました")
            return
        
        # 画像生成器とWordPressクライアントを初期化
        image_generator = ImageGenerator(config)
        wp_client = WordPressClient(config)
        
        # 記事データとセクションを作成
        article_data, sections = create_bitcoin_ath_article()
        
        # アイキャッチ画像を生成
        logger.info("アイキャッチ画像生成中...")
        featured_image = image_generator.generate_featured_image(
            article_data['title'],
            ' '.join([s['content'] for s in sections[:2]])  # 最初の2セクションを使用
        )
        
        # セクション画像を生成
        logger.info("セクション画像生成中...")
        section_images = image_generator.generate_section_images(sections)
        
        # 記事本文を構築（画像付き）
        content_html = ""
        
        for i, section in enumerate(sections):
            content_html += f'<h2>{section["title"]}</h2>\n\n'
            content_html += f'<p>{section["content"]}</p>\n\n'
            
            # 対応するセクション画像があれば挿入
            for img in section_images:
                if img['section_index'] == i:
                    content_html += f'<figure class="wp-block-image size-large">\n'
                    content_html += f'<img src="{img["local_path"]}" alt="{img["section_title"]}" class="section-image" />\n'
                    content_html += f'<figcaption>図{i+1}: {img["section_title"]}</figcaption>\n'
                    content_html += f'</figure>\n\n'
                    break
        
        # 記事データを更新
        article_data['content'] = content_html
        article_data['word_count'] = len(content_html.replace(' ', '').replace('\n', ''))
        
        # アイキャッチ画像情報を追加
        if featured_image:
            article_data['featured_image'] = featured_image
        
        # セクション画像情報を追加
        article_data['section_images'] = section_images
        
        # SEO情報を追加
        article_data['seo'] = {
            'focus_keyword': 'ビットコイン',
            'meta_title': 'ビットコイン史上最高値11.8万ドル突破｜ETF流入で大相場',
            'meta_description': 'ビットコインが史上最高値11.8万ドルを突破！機関投資家のETF流入11.8億ドルが支える大相場の背景と今後の展望を詳しく解説します。',
            'meta_keywords': ['ビットコイン', '史上最高値', 'ETF', '機関投資', '11万8千ドル', '仮想通貨', 'BTC', '投資']
        }
        
        # 生成結果をJSONファイルに保存
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'generated_bitcoin_ath_article_with_images_{timestamp}.json'
        
        # JSON保存用にdatetimeオブジェクトを文字列に変換
        save_data = article_data.copy()
        if 'generation_date' in save_data:
            save_data['generation_date'] = save_data['generation_date'].isoformat()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        # プレビューHTMLを作成
        preview_file = f'bitcoin_ath_article_preview_{timestamp}.html'
        create_preview_html(article_data, preview_file)
        
        logger.info(f"画像付き記事生成完了")
        logger.info(f"記事データ: {output_file}")
        logger.info(f"プレビュー: {preview_file}")
        logger.info(f"文字数: {article_data['word_count']}文字")
        logger.info(f"生成画像数: {len(section_images) + (1 if featured_image else 0)}枚")
        
        # WordPress投稿オプション
        print("\n" + "="*60)
        print("📝 画像付き記事生成完了！")
        print("="*60)
        print(f"📄 記事ファイル: {output_file}")
        print(f"🖼️  プレビュー: {preview_file}")
        print(f"📊 文字数: {article_data['word_count']:,}文字")
        print(f"🎨 生成画像: {len(section_images) + (1 if featured_image else 0)}枚")
        print(f"⭐ 重要度スコア: {article_data['importance_score']}/100")
        print("\nWordPressに投稿しますか？ (y/n): ", end="")
        
        user_input = input().strip().lower()
        if user_input == 'y':
            publish_to_wordpress(article_data, wp_client, image_generator)
        else:
            print("記事データが保存されました。後でWordPressに投稿できます。")
        
    except Exception as e:
        logger.error(f"画像付き記事生成エラー: {e}")

def create_preview_html(article_data, filename):
    """プレビューHTML作成"""
    html_content = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article_data['title']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
               line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #2c5aa0; border-bottom: 3px solid #f7931a; padding-bottom: 10px; }}
        h2 {{ color: #333; border-left: 4px solid #f7931a; padding-left: 15px; }}
        .meta {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .section-image {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        figure {{ text-align: center; margin: 20px 0; }}
        figcaption {{ font-style: italic; color: #666; margin-top: 8px; }}
    </style>
</head>
<body>
    <h1>{article_data['title']}</h1>
    
    <div class="meta">
        <strong>📊 記事情報</strong><br>
        文字数: {article_data.get('word_count', 0):,}文字<br>
        重要度: {article_data.get('importance_score', 0)}/100<br>
        カテゴリ: {article_data.get('category', '')}<br>
        タグ: {', '.join(article_data.get('tags', []))}<br>
        生成日時: {article_data.get('generation_date', '').isoformat() if hasattr(article_data.get('generation_date', ''), 'isoformat') else str(article_data.get('generation_date', ''))}
    </div>
    
    {article_data.get('content', '')}
    
    <hr>
    <p><small>🤖 Generated with Claude Code | 画像生成: OpenAI DALL-E 3</small></p>
</body>
</html>
"""
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

def publish_to_wordpress(article_data, wp_client, image_generator):
    """WordPressに画像付き記事を投稿"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("WordPress投稿を開始...")
        
        # WordPressに画像をアップロード
        uploaded_media_ids = []
        
        # アイキャッチ画像をアップロード
        featured_media_id = None
        if article_data.get('featured_image'):
            featured_media_id = image_generator.upload_image_to_wordpress(
                article_data['featured_image']['local_path'], 
                wp_client
            )
        
        # セクション画像をアップロード
        for image in article_data.get('section_images', []):
            media_id = image_generator.upload_image_to_wordpress(
                image['local_path'], 
                wp_client
            )
            if media_id:
                uploaded_media_ids.append(media_id)
        
        # 記事データを更新（WordPressメディアIDを使用）
        if featured_media_id:
            article_data['featured_media'] = featured_media_id
        
        # 記事を投稿
        result = wp_client.publish_article(article_data)
        
        if result and result.get('success'):
            logger.info(f"WordPress投稿成功: {result.get('url')}")
            print(f"\n✅ WordPress投稿成功！")
            print(f"📝 投稿ID: {result.get('id')}")
            print(f"🌐 URL: {result.get('url')}")
        else:
            logger.error("WordPress投稿失敗")
            print("❌ WordPress投稿に失敗しました")
        
    except Exception as e:
        logger.error(f"WordPress投稿エラー: {e}")
        print(f"❌ WordPress投稿エラー: {e}")

if __name__ == "__main__":
    generate_article_with_images()