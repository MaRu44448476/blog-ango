#!/usr/bin/env python3
"""
既存の画像付き記事をWordPressに投稿するスクリプト
"""

import logging
import sys
import os
import json
from datetime import datetime

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
            logging.FileHandler('logs/wordpress_publish.log'),
            logging.StreamHandler()
        ]
    )

def publish_existing_article():
    """既存の画像付き記事をWordPressに投稿"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("既存記事のWordPress投稿を開始")
    
    try:
        # 設定とクライアントを初期化
        config = Config()
        if not config.validate_config():
            logger.error("設定の検証に失敗しました")
            return
        
        image_generator = ImageGenerator(config)
        wp_client = WordPressClient(config)
        
        # WordPress接続テスト
        if not wp_client.test_connection():
            logger.error("WordPress接続に失敗しました")
            print("❌ WordPress接続エラー")
            print("📝 .envファイルのWordPress設定を確認してください:")
            print("   WP_URL=https://your-site.com")
            print("   WP_USERNAME=your_username") 
            print("   WP_PASSWORD=your_app_password")
            return
        
        # 最新の記事データを読み込み
        article_file = "generated_bitcoin_ath_article_with_images_20250713_235220.json"
        
        if not os.path.exists(article_file):
            logger.error(f"記事ファイルが見つかりません: {article_file}")
            return
        
        with open(article_file, 'r', encoding='utf-8') as f:
            article_data = json.load(f)
        
        logger.info(f"記事データ読み込み完了: {article_data.get('title', 'No Title')}")
        
        # 画像ファイルのパスを更新
        image_dir = "generated_images"
        image_files = [
            "featured_20250713_234914.png",
            "section_1_20250713_234943.png", 
            "section_2_20250713_235007.png",
            "section_3_20250713_235028.png",
            "section_4_20250713_235051.png",
            "section_5_20250713_235108.png",
            "section_6_20250713_235130.png",
            "section_7_20250713_235156.png",
            "section_8_20250713_235214.png"
        ]
        
        # WordPressに画像をアップロード
        logger.info("画像をWordPressにアップロード中...")
        uploaded_media_ids = []
        featured_media_id = None
        
        for i, image_file in enumerate(image_files):
            image_path = os.path.join(image_dir, image_file)
            
            if not os.path.exists(image_path):
                logger.warning(f"画像ファイルが見つかりません: {image_path}")
                continue
            
            logger.info(f"画像アップロード中 ({i+1}/{len(image_files)}): {image_file}")
            
            media_id = image_generator.upload_image_to_wordpress(image_path, wp_client)
            
            if media_id:
                if i == 0:  # 最初の画像をアイキャッチに設定
                    featured_media_id = media_id
                    logger.info(f"アイキャッチ画像設定: Media ID {media_id}")
                else:
                    uploaded_media_ids.append(media_id)
                
                logger.info(f"画像アップロード成功: Media ID {media_id}")
            else:
                logger.error(f"画像アップロード失敗: {image_file}")
        
        # 記事本文に画像IDを埋め込み
        content = article_data.get('content', '')
        
        # セクション画像を記事に埋め込み
        sections = [
            "【速報】ビットコイン11.8万ドル突破の瞬間",
            "ETF大量流入が史上最高値を後押し", 
            "市場への三段階影響分析",
            "専門家の見解：強気と慎重論",
            "国際動向：世界各国の反応",
            "投資家向け具体的アドバイス",
            "よくある質問（Q&A）",
            "まとめ：新時代の始まり"
        ]
        
        # WordPressギャラリー形式で画像を挿入
        updated_content = ""
        section_index = 0
        
        for line in content.split('\n'):
            updated_content += line + '\n'
            
            # セクションタイトルの後に画像を挿入
            if any(section in line for section in sections) and '<h2>' in line:
                if section_index < len(uploaded_media_ids):
                    media_id = uploaded_media_ids[section_index]
                    updated_content += f'\n<!-- wp:image {{"id":{media_id},"sizeSlug":"large"}} -->\n'
                    updated_content += f'<figure class="wp-block-image size-large">'
                    updated_content += f'<img src="[wp-image-{media_id}]" alt="図{section_index+1}: {sections[section_index]}" class="wp-image-{media_id}"/>'
                    updated_content += f'</figure>\n'
                    updated_content += f'<!-- /wp:image -->\n\n'
                    section_index += 1
        
        # 記事データを更新
        article_data['content'] = updated_content
        if featured_media_id:
            article_data['featured_media'] = featured_media_id
        
        # WordPressに投稿
        logger.info("記事をWordPressに投稿中...")
        result = wp_client.publish_article(article_data)
        
        if result and result.get('success'):
            logger.info(f"WordPress投稿成功: {result.get('url')}")
            
            print("\n" + "="*60)
            print("🎉 画像付き記事投稿成功！")
            print("="*60)
            print(f"📝 投稿ID: {result.get('id')}")
            print(f"🌐 URL: {result.get('url')}")
            print(f"📊 文字数: {article_data.get('word_count', 0):,}文字")
            print(f"🎨 アップロード画像: {len(uploaded_media_ids) + (1 if featured_media_id else 0)}枚")
            print(f"⭐ 重要度スコア: {article_data.get('importance_score', 0)}/100")
            print(f"📅 投稿日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
            
            # 投稿履歴を保存
            history = {
                'timestamp': datetime.now().isoformat(),
                'post_id': result.get('id'),
                'url': result.get('url'),
                'title': article_data.get('title'),
                'word_count': article_data.get('word_count'),
                'images_count': len(uploaded_media_ids) + (1 if featured_media_id else 0),
                'importance_score': article_data.get('importance_score')
            }
            
            try:
                with open('publish_history.json', 'r', encoding='utf-8') as f:
                    publish_history = json.load(f)
            except:
                publish_history = []
            
            publish_history.append(history)
            
            with open('publish_history.json', 'w', encoding='utf-8') as f:
                json.dump(publish_history, f, ensure_ascii=False, indent=2)
            
        else:
            logger.error("WordPress投稿失敗")
            print("❌ WordPress投稿に失敗しました")
            if result:
                print(f"エラー: {result.get('error_message', 'Unknown error')}")
        
    except Exception as e:
        logger.error(f"記事投稿エラー: {e}")
        print(f"❌ エラーが発生しました: {e}")

if __name__ == "__main__":
    publish_existing_article()