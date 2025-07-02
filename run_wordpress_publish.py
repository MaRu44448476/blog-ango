#!/usr/bin/env python3
"""
WordPress記事投稿実行スクリプト
"""

import json
import sys
import urllib.request
import base64
import glob
import os

# WordPress設定
WP_URL = "https://crypto-dictionary.net"
WP_USERNAME = "MaRu"
WP_PASSWORD = "3sMS 8JWd xS8k OkOZ qhX2 3u4z"

def load_latest_article():
    """最新の記事データを読み込み"""
    
    # generated_article_*.jsonファイルを探す
    article_files = glob.glob("generated_article_*.json")
    
    if not article_files:
        print("❌ 生成された記事が見つかりません")
        print("まず run_article_generation.py を実行してください")
        return None
    
    # 最新のファイルを取得
    latest_file = max(article_files, key=os.path.getctime)
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            article = json.load(f)
        
        print(f"📄 記事データを読み込み: {latest_file}")
        print(f"📝 タイトル: {article['title']}")
        print(f"📊 文字数: {article['word_count']}字")
        print(f"🏷️ カテゴリ: {article['category']}")
        
        return article
    except Exception as e:
        print(f"❌ 記事データ読み込みエラー: {e}")
        return None

def get_or_create_category(category_name):
    """カテゴリを取得または作成"""
    
    credentials = f"{WP_USERNAME}:{WP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json',
        'User-Agent': 'CryptoMediaSystem/1.0'
    }
    
    # 既存カテゴリを検索
    categories_url = f"{WP_URL}/wp-json/wp/v2/categories?search={category_name}"
    
    try:
        request = urllib.request.Request(categories_url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.getcode() == 200:
                categories = json.loads(response.read().decode())
                
                # 完全一致するカテゴリを探す
                for category in categories:
                    if category['name'] == category_name:
                        print(f"✅ 既存カテゴリを使用: {category_name} (ID: {category['id']})")
                        return category['id']
        
        # カテゴリが存在しない場合は作成
        print(f"📝 新しいカテゴリを作成: {category_name}")
        
        category_data = {
            'name': category_name,
            'slug': category_name.lower().replace(' ', '-').replace('・', '-')
        }
        
        create_url = f"{WP_URL}/wp-json/wp/v2/categories"
        post_data = json.dumps(category_data).encode('utf-8')
        
        request = urllib.request.Request(create_url, data=post_data, headers=headers, method='POST')
        
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.getcode() in [200, 201]:
                new_category = json.loads(response.read().decode())
                print(f"✅ カテゴリ作成成功: {category_name} (ID: {new_category['id']})")
                return new_category['id']
        
    except Exception as e:
        print(f"⚠️ カテゴリ処理エラー: {e}")
        
    return None

def publish_article_to_wordpress(article):
    """記事をWordPressに投稿"""
    
    credentials = f"{WP_USERNAME}:{WP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json',
        'User-Agent': 'CryptoMediaSystem/1.0'
    }
    
    # カテゴリIDを取得
    category_id = get_or_create_category(article['category'])
    
    # 投稿データを準備
    post_data = {
        'title': article['title'],
        'content': article['content'],
        'status': 'draft',  # 安全のため下書きとして投稿
        'categories': [category_id] if category_id else [],
        'excerpt': f"自動生成された{article['article_type']}記事です。文字数: {article['word_count']}字"
    }
    
    posts_url = f"{WP_URL}/wp-json/wp/v2/posts"
    
    print("\n📤 WordPressに記事を投稿中...")
    print(f"📝 タイトル: {article['title']}")
    print(f"📊 ステータス: {post_data['status']} (下書き)")
    
    try:
        json_data = json.dumps(post_data).encode('utf-8')
        request = urllib.request.Request(posts_url, data=json_data, headers=headers, method='POST')
        
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.getcode() in [200, 201]:
                result = json.loads(response.read().decode())
                
                print("✅ WordPress投稿成功！")
                print(f"🆔 投稿ID: {result.get('id')}")
                print(f"🔗 投稿URL: {result.get('link')}")
                print(f"📅 作成日: {result.get('date')}")
                print(f"✏️ 編集URL: {WP_URL}/wp-admin/post.php?post={result.get('id')}&action=edit")
                
                return result
            else:
                print(f"❌ 投稿失敗: HTTP {response.getcode()}")
                return None
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP エラー: {e.code}")
        try:
            error_detail = e.read().decode()
            error_data = json.loads(error_detail)
            print(f"エラーコード: {error_data.get('code', 'unknown')}")
            print(f"エラーメッセージ: {error_data.get('message', 'unknown')}")
        except:
            print(f"エラー詳細: {error_detail if hasattr(e, 'read') else 'なし'}")
        return None
        
    except Exception as e:
        print(f"❌ 投稿エラー: {e}")
        return None

def list_available_articles():
    """利用可能な記事一覧を表示"""
    article_files = glob.glob("generated_article_*.json")
    
    if not article_files:
        print("❌ 生成された記事がありません")
        return []
    
    print("\n📄 利用可能な記事:")
    articles = []
    
    for i, file_path in enumerate(sorted(article_files, key=os.path.getctime, reverse=True), 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                article = json.load(f)
            
            print(f"{i}. {article['title'][:60]}{'...' if len(article['title']) > 60 else ''}")
            print(f"   タイプ: {article['article_type']} | 文字数: {article['word_count']}字")
            print(f"   ファイル: {file_path}")
            
            articles.append((file_path, article))
            
        except Exception as e:
            print(f"   ❌ エラー: {e}")
    
    return articles

def main():
    """メイン実行"""
    print("🚀 WordPress記事投稿システム")
    print("="*50)
    
    # 利用可能な記事を一覧表示
    articles = list_available_articles()
    
    if not articles:
        print("記事を生成してから再実行してください: python3 run_article_generation.py")
        return
    
    # 最新の記事を自動選択
    latest_file, latest_article = articles[0]
    
    print(f"\n📝 最新の記事を投稿します:")
    print(f"タイトル: {latest_article['title']}")
    print(f"タイプ: {latest_article['article_type']}")
    print(f"文字数: {latest_article['word_count']}字")
    
    # 投稿実行
    result = publish_article_to_wordpress(latest_article)
    
    if result:
        print("\n🎉 投稿完了！")
        print("\n📋 次のステップ:")
        print("1. WordPressダッシュボードで記事を確認")
        print("2. 内容に問題がなければ「公開」に変更")
        print("3. カテゴリやタグを調整")
        print("4. アイキャッチ画像を設定（必要に応じて）")
        
        # 投稿履歴を保存
        save_publish_history(latest_article, result)
        
    else:
        print("\n❌ 投稿に失敗しました")
        print("WordPress設定やAPI権限を確認してください")

def save_publish_history(article, wp_result):
    """投稿履歴を保存"""
    history = {
        'article_title': article['title'],
        'article_type': article['article_type'],
        'word_count': article['word_count'],
        'wp_post_id': wp_result.get('id'),
        'wp_url': wp_result.get('link'),
        'publish_date': wp_result.get('date'),
        'status': wp_result.get('status')
    }
    
    try:
        # 既存の履歴を読み込み
        try:
            with open('publish_history.json', 'r', encoding='utf-8') as f:
                all_history = json.load(f)
        except FileNotFoundError:
            all_history = []
        
        # 新しい履歴を追加
        all_history.append(history)
        
        # 履歴を保存
        with open('publish_history.json', 'w', encoding='utf-8') as f:
            json.dump(all_history, f, ensure_ascii=False, indent=2)
        
        print(f"📋 投稿履歴を保存しました")
        
    except Exception as e:
        print(f"⚠️ 履歴保存エラー: {e}")

if __name__ == "__main__":
    main()