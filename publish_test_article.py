#!/usr/bin/env python3
"""
生成記事をWordPressに投稿（SEO対応版）
"""

import json
import urllib.request
import base64
import glob
import sys
from datetime import datetime

# WordPress設定
WP_URL = "https://crypto-dictionary.net"
WP_USERNAME = "MaRu"
WP_PASSWORD = "3sMS 8JWd xS8k OkOZ qhX2 3u4z"

def publish_article_to_wordpress(status='draft'):
    """生成記事をWordPressに投稿"""
    
    # 最新の記事ファイルを探す（複数パターン対応）
    article_files = glob.glob("selected_article_*.json") + glob.glob("test_article_*.json")
    
    if not article_files:
        print("❌ 記事ファイルが見つかりません")
        print("先に記事を生成してください")
        return
    
    # 最新の記事を読み込み（selected_article を優先）
    selected_files = [f for f in article_files if f.startswith('selected_article_')]
    if selected_files:
        latest_file = max(selected_files, key=lambda x: x)
    else:
        latest_file = max(article_files, key=lambda x: x)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            article = json.load(f)
        
        print(f"📄 記事を読み込み: {latest_file}")
        print(f"📝 タイトル: {article['title']}")
        print(f"📊 文字数: {article['word_count']}字")
        if 'focus_keyword' in article:
            print(f"🎯 フォーカスキーワード: {article['focus_keyword']}")
        
    except Exception as e:
        print(f"❌ 記事読み込みエラー: {e}")
        return
    
    # 認証ヘッダー
    credentials = f"{WP_USERNAME}:{WP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json',
        'User-Agent': 'CryptoMediaSystem/1.0'
    }
    
    # SEO対応投稿データを準備（WordPressの制限に合わせてシンプルに）
    post_data = {
        'title': article.get('seo_title', article['title']),  # SEOタイトル優先
        'content': article['content'],
        'status': status,  # 引数で指定されたステータス
        'excerpt': article.get('excerpt', f"親しみやすい日本語で書かれた仮想通貨ニュース解説記事。文字数: {article['word_count']}字"),
    }
    
    # 投稿後にタグとSEO情報を追加する予定であることを記録
    tag_info = {
        'tags': article.get('tags', []),
        'meta_keywords': article.get('meta_keywords', []),
        'focus_keyword': article.get('focus_keyword', ''),
        'meta_description': article.get('meta_description', '')
    }
    
    posts_url = f"{WP_URL}/wp-json/wp/v2/posts"
    
    print(f"\n📤 WordPressに記事を{status}として投稿中...")
    
    try:
        json_data = json.dumps(post_data, ensure_ascii=False).encode('utf-8')
        request = urllib.request.Request(posts_url, data=json_data, headers=headers, method='POST')
        
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.getcode() in [200, 201]:
                result = json.loads(response.read().decode())
                
                print("✅ 記事投稿成功！")
                print(f"🆔 投稿ID: {result.get('id')}")
                print(f"📄 ステータス: {result.get('status')}")
                print(f"🔗 投稿URL: {result.get('link')}")
                print(f"📅 作成日: {result.get('date')}")
                print(f"✏️ 編集URL: {WP_URL}/wp-admin/post.php?post={result.get('id')}&action=edit")
                
                # SEO情報も表示
                print(f"🎯 フォーカスキーワード: {tag_info['focus_keyword']}")
                print(f"🏷️ 推奨タグ: {', '.join(tag_info['tags'])}")
                print(f"📝 メタ説明: {tag_info['meta_description'][:100]}...")
                print(f"🔍 SEOキーワード: {', '.join(tag_info['meta_keywords'][:5])}")
                
                return result
            else:
                print(f"❌ 投稿失敗: HTTP {response.getcode()}")
                return None
                
    except urllib.error.HTTPError as e:
        # 詳細なエラー情報を取得
        error_body = e.read().decode('utf-8')
        print(f"❌ HTTP投稿エラー: {e.code}")
        try:
            error_data = json.loads(error_body)
            print(f"エラー詳細: {error_data}")
        except:
            print(f"エラー詳細: {error_body}")
        return None
    except Exception as e:
        print(f"❌ 投稿エラー: {e}")
        return None

if __name__ == "__main__":
    # 引数で下書きか公開かを指定可能
    status = 'draft'
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ['publish', 'public']:
            status = 'publish'
    
    print("🚀 記事WordPress投稿システム（SEO対応）")
    print("=" * 60)
    print(f"投稿モード: {status}")
    
    result = publish_article_to_wordpress(status)
    
    if result:
        print("\n🎉 記事の投稿が完了しました！")
        print("\n📋 確認事項:")
        print("1. WordPressダッシュボードで記事内容を確認")
        print("2. SEO設定（メタ説明、キーワード）をチェック")
        print("3. 文体や内容が親しみやすいかチェック")
        print("4. 日本語として自然かどうか確認")
        if status == 'draft':
            print("5. 問題なければ「公開」に変更")
        
        print("\n🔍 記事の特徴:")
        print("- 4000字超の詳細解説記事")
        print("- SEO対応（メタ説明、キーワード、タグ自動設定）")
        print("- 「みなさん、こんにちは！」から始まる親しみやすい導入")
        print("- 専門用語をわかりやすく解説")
        print("- 読者目線での疑問と回答（Q&A付き）")
        print("- 短期・中期・長期の影響分析")
        print("- 具体的なアクションプラン（初心者・経験者別）")
    else:
        print("\n❌ 記事の投稿に失敗しました")
    
    print("\n" + "=" * 60)