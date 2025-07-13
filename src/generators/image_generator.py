"""
画像生成モジュール
OpenAI DALL-E APIを使用してアイキャッチ画像や段落用画像を生成
"""

import logging
import requests
import base64
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
import json

class ImageGenerator:
    """OpenAI DALL-E画像生成クラス"""
    
    def __init__(self, config):
        """
        画像生成器を初期化
        
        Args:
            config: 設定オブジェクト
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_key = config.OPENAI_API_KEY
        
        # 画像保存ディレクトリ
        self.image_dir = "generated_images"
        os.makedirs(self.image_dir, exist_ok=True)
        
        # DALL-E API設定
        self.dalle_url = "https://api.openai.com/v1/images/generations"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_featured_image(self, article_title: str, article_content: str) -> Optional[Dict[str, Any]]:
        """
        記事のアイキャッチ画像を生成
        
        Args:
            article_title: 記事タイトル
            article_content: 記事内容
            
        Returns:
            Dict: 生成された画像情報
        """
        try:
            self.logger.info(f"アイキャッチ画像生成開始: {article_title}")
            
            # プロンプトを作成
            prompt = self._create_featured_image_prompt(article_title, article_content)
            
            # 画像を生成
            image_data = self._generate_image(
                prompt=prompt,
                size="1792x1024",  # WordPress推奨のアイキャッチサイズ
                quality="hd",
                style="vivid"
            )
            
            if image_data:
                # 画像を保存
                filename = f"featured_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = os.path.join(self.image_dir, filename)
                
                if self._save_image(image_data['url'], filepath):
                    self.logger.info(f"アイキャッチ画像生成完了: {filepath}")
                    return {
                        'type': 'featured',
                        'prompt': prompt,
                        'url': image_data['url'],
                        'local_path': filepath,
                        'filename': filename,
                        'size': "1792x1024"
                    }
            
        except Exception as e:
            self.logger.error(f"アイキャッチ画像生成エラー: {e}")
        
        return None
    
    def generate_section_images(self, article_sections: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        記事の各セクション用画像を生成
        
        Args:
            article_sections: セクション情報のリスト
            
        Returns:
            List[Dict]: 生成された画像情報のリスト
        """
        generated_images = []
        
        for i, section in enumerate(article_sections):
            try:
                self.logger.info(f"セクション画像生成中 ({i+1}/{len(article_sections)}): {section.get('title', '')}")
                
                # プロンプトを作成
                prompt = self._create_section_image_prompt(section)
                
                # 画像を生成
                image_data = self._generate_image(
                    prompt=prompt,
                    size="1024x1024",  # 正方形画像
                    quality="standard",
                    style="natural"
                )
                
                if image_data:
                    # 画像を保存
                    filename = f"section_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    filepath = os.path.join(self.image_dir, filename)
                    
                    if self._save_image(image_data['url'], filepath):
                        generated_images.append({
                            'type': 'section',
                            'section_index': i,
                            'section_title': section.get('title', ''),
                            'prompt': prompt,
                            'url': image_data['url'],
                            'local_path': filepath,
                            'filename': filename,
                            'size': "1024x1024"
                        })
                
                # レート制限対策
                import time
                time.sleep(2)
                
            except Exception as e:
                self.logger.error(f"セクション画像生成エラー ({i+1}): {e}")
                continue
        
        self.logger.info(f"セクション画像生成完了: {len(generated_images)}/{len(article_sections)} 件成功")
        return generated_images
    
    def _generate_image(self, prompt: str, size: str = "1024x1024", 
                       quality: str = "standard", style: str = "vivid") -> Optional[Dict[str, Any]]:
        """
        DALL-E APIを使用して画像を生成
        
        Args:
            prompt: 画像生成プロンプト
            size: 画像サイズ
            quality: 画像品質
            style: 画像スタイル
            
        Returns:
            Dict: 生成された画像データ
        """
        try:
            payload = {
                "model": "dall-e-3",
                "prompt": prompt,
                "n": 1,
                "size": size,
                "quality": quality,
                "style": style
            }
            
            response = requests.post(
                self.dalle_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['data'][0]
            else:
                self.logger.error(f"DALL-E API エラー: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.logger.error(f"画像生成リクエストエラー: {e}")
        
        return None
    
    def _save_image(self, image_url: str, filepath: str) -> bool:
        """
        画像URLから画像をダウンロードして保存
        
        Args:
            image_url: 画像URL
            filepath: 保存先パス
            
        Returns:
            bool: 保存が成功したかどうか
        """
        try:
            response = requests.get(image_url, timeout=30)
            
            if response.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                self.logger.info(f"画像保存完了: {filepath}")
                return True
            else:
                self.logger.error(f"画像ダウンロードエラー: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"画像保存エラー: {e}")
        
        return False
    
    def _create_featured_image_prompt(self, title: str, content: str) -> str:
        """
        アイキャッチ画像用プロンプトを作成
        
        Args:
            title: 記事タイトル
            content: 記事内容
            
        Returns:
            str: 画像生成プロンプト
        """
        # タイトルからキーワードを抽出
        keywords = []
        if 'ビットコイン' in title or 'bitcoin' in title.lower():
            keywords.append('Bitcoin')
        if '最高値' in title or 'high' in title.lower():
            keywords.append('all-time high')
        if 'ETF' in title:
            keywords.append('ETF')
        
        prompt = f"""
Create a professional, modern financial illustration for a cryptocurrency news article.
The image should represent: Bitcoin reaching new all-time highs above $118,000.

Style: Clean, professional, financial news aesthetic
Elements: Bitcoin logo/symbol, upward trending charts, golden/orange color scheme
Mood: Success, growth, breakthrough
Format: Horizontal banner suitable for article header
Text: No text in the image

The illustration should convey: Record-breaking price achievement, institutional confidence, market momentum
Visual elements: Rising price charts, Bitcoin symbol, financial graphics, professional trading dashboard aesthetic
"""
        
        return prompt
    
    def _create_section_image_prompt(self, section: Dict[str, str]) -> str:
        """
        セクション用画像プロンプトを作成
        
        Args:
            section: セクション情報
            
        Returns:
            str: 画像生成プロンプト
        """
        title = section.get('title', '')
        content = section.get('content', '')
        
        # セクションの内容に基づいてプロンプトを生成
        if '市場' in title or 'market' in title.lower():
            base_prompt = "Financial market trading charts and graphs"
        elif 'ETF' in title:
            base_prompt = "Professional investment funds and institutional trading"
        elif '影響' in title or 'impact' in title.lower():
            base_prompt = "Economic impact visualization with arrows and connections"
        elif '専門家' in title or 'expert' in title.lower():
            base_prompt = "Professional financial analysts and business meeting"
        elif '国際' in title or 'global' in title.lower():
            base_prompt = "Global financial networks and world map"
        elif 'アドバイス' in title or 'advice' in title.lower():
            base_prompt = "Financial planning and investment strategy"
        elif 'Q&A' in title:
            base_prompt = "Question and answer, FAQ concept illustration"
        elif 'まとめ' in title or 'summary' in title.lower():
            base_prompt = "Summary infographic with key points"
        else:
            base_prompt = "Modern cryptocurrency and blockchain technology"
        
        prompt = f"""
Create a clean, professional illustration for a cryptocurrency article section.
Theme: {base_prompt}
Style: Modern, minimalist, financial industry aesthetic
Colors: Blue and orange color scheme, professional look
Format: Square image suitable for article content
Text: No text in the image
Mood: Professional, informative, trustworthy
"""
        
        return prompt
    
    def upload_image_to_wordpress(self, image_path: str, wp_client) -> Optional[int]:
        """
        生成した画像をWordPressにアップロード
        
        Args:
            image_path: ローカル画像パス
            wp_client: WordPressクライアント
            
        Returns:
            int: WordPressメディアID
        """
        try:
            # WordPressメディアAPIを使用して画像をアップロード
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            filename = os.path.basename(image_path)
            
            # メディアアップロード用のヘッダー
            headers = wp_client.headers.copy()
            headers['Content-Type'] = 'image/png'
            headers['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            # WordPressメディアエンドポイントにアップロード
            media_url = f"{wp_client.api_base}/media"
            
            response = requests.post(
                media_url,
                headers=headers,
                data=image_data,
                timeout=60
            )
            
            if response.status_code == 201:
                media_data = response.json()
                media_id = media_data['id']
                self.logger.info(f"WordPress画像アップロード成功: ID {media_id}")
                return media_id
            else:
                self.logger.error(f"WordPress画像アップロードエラー: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"WordPress画像アップロードエラー: {e}")
        
        return None
    
    def create_image_gallery_html(self, images: List[Dict[str, Any]], 
                                 wp_media_ids: List[int] = None) -> str:
        """
        画像ギャラリー用HTMLを作成
        
        Args:
            images: 画像情報のリスト
            wp_media_ids: WordPressメディアIDのリスト
            
        Returns:
            str: HTMLコード
        """
        gallery_html = ""
        
        for i, image in enumerate(images):
            if image['type'] == 'section':
                # セクション画像用HTML
                alt_text = f"Section {image['section_index'] + 1}: {image['section_title']}"
                
                if wp_media_ids and i < len(wp_media_ids):
                    # WordPressメディアIDを使用
                    gallery_html += f'\n<figure class="wp-block-image size-large">\n'
                    gallery_html += f'<img src="[wp-media-{wp_media_ids[i]}]" alt="{alt_text}" />\n'
                    gallery_html += f'</figure>\n'
                else:
                    # ローカルパスを使用（テスト用）
                    gallery_html += f'\n<figure class="wp-block-image size-large">\n'
                    gallery_html += f'<img src="{image["local_path"]}" alt="{alt_text}" />\n'
                    gallery_html += f'</figure>\n'
        
        return gallery_html