#!/usr/bin/env python3
"""
クレジット表記なしの記事生成テンプレート作成
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
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_clean_article_template():
    """クレジット表記なしの記事テンプレートを作成"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # クリーンな記事テンプレート設定を保存
    clean_settings = {
        "article_generation": {
            "include_credits": False,
            "include_footer": False,
            "clean_output": True
        },
        "image_generation": {
            "include_watermark": False,
            "clean_captions": True
        },
        "wordpress_publishing": {
            "clean_content": True,
            "remove_system_tags": True
        }
    }
    
    # 設定を保存
    with open('clean_article_settings.json', 'w', encoding='utf-8') as f:
        json.dump(clean_settings, f, ensure_ascii=False, indent=2)
    
    print("✅ クリーンな記事生成設定を保存しました")
    print("📁 ファイル: clean_article_settings.json")
    print("🚀 今後の記事生成ではクレジット表記が含まれません")
    
    # 記事生成関数のテンプレートも更新
    clean_template = '''
def generate_clean_article_content(sections, media_urls):
    """クレジット表記なしの記事コンテンツを生成"""
    
    content = ""
    
    for i, section in enumerate(sections):
        content += f"<h2>{section['title']}</h2>\\n\\n"
        content += f"<p>{section['content']}</p>\\n\\n"
        
        # 対応する画像があれば追加
        section_key = f"section_{i+1}"
        if section_key in media_urls:
            content += f"""<figure class="wp-block-image size-large aligncenter">
<img src="{media_urls[section_key]['url']}" alt="{section['title']}" class="wp-image-{media_urls[section_key]['id']}"/>
<figcaption>図{i+1}: {section['title']}</figcaption>
</figure>\\n\\n"""
    
    # 免責事項のみ追加（クレジット表記なし）
    content += """<p><strong>【重要な免責事項】</strong><br>
本記事は情報提供を目的としており、投資助言ではありません。仮想通貨投資にはリスクが伴いますので、投資判断は自己責任でお願いします。</p>"""
    
    return content
'''
    
    with open('clean_article_template.py', 'w', encoding='utf-8') as f:
        f.write(clean_template)
    
    logger.info("クリーンな記事テンプレートを作成しました")
    print("📝 テンプレート: clean_article_template.py")

if __name__ == "__main__":
    create_clean_article_template()