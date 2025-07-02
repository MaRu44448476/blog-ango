#!/usr/bin/env python3
"""
簡単なWordPress接続テスト（依存関係最小限）
"""

import base64
import json
try:
    import urllib.request
    import urllib.parse
    import urllib.error
except ImportError:
    print("❌ urllib モジュールが利用できません")
    exit(1)

# WordPress設定
WP_URL = "https://crypto-dictionary.net"
WP_USERNAME = "MaRu"
WP_PASSWORD = "3sMS 8JWd xS8k OkOZ qhX2 3u4z"

def test_wordpress_connection():
    """WordPress REST API接続テスト"""
    
    # 認証ヘッダーの作成
    credentials = f"{WP_USERNAME}:{WP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json',
        'User-Agent': 'CryptoMediaSystem/1.0'
    }
    
    # REST APIエンドポイント
    api_url = f"{WP_URL}/wp-json/wp/v2"
    
    print("🔗 WordPress接続テスト中...")
    print(f"URL: {WP_URL}")
    print(f"ユーザー: {WP_USERNAME}")
    print(f"API: {api_url}")
    
    try:
        # サイト情報を取得
        request = urllib.request.Request(api_url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode())
                
                print("✅ WordPress REST API接続成功！")
                print(f"サイト名: {data.get('name', '不明')}")
                print(f"説明: {data.get('description', '不明')}")
                print(f"URL: {data.get('url', '不明')}")
                
                return True
            else:
                print(f"❌ 接続失敗: HTTP {response.getcode()}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP エラー: {e.code}")
        if e.code == 401:
            print("認証エラー: ユーザー名またはアプリケーションパスワードが間違っています")
        elif e.code == 403:
            print("権限エラー: ユーザーに適切な権限がありません")
        elif e.code == 404:
            print("エラー: WordPress REST APIが見つかりません")
        
        print(f"エラー詳細: {e.read().decode() if hasattr(e, 'read') else 'なし'}")
        return False
        
    except urllib.error.URLError as e:
        print(f"❌ URL エラー: {e.reason}")
        return False
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False

def test_posts_endpoint():
    """投稿エンドポイントのテスト"""
    
    credentials = f"{WP_USERNAME}:{WP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json',
        'User-Agent': 'CryptoMediaSystem/1.0'
    }
    
    posts_url = f"{WP_URL}/wp-json/wp/v2/posts"
    
    print("\n📝 投稿エンドポイントテスト中...")
    
    try:
        request = urllib.request.Request(posts_url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.getcode() == 200:
                posts = json.loads(response.read().decode())
                
                print(f"✅ 投稿エンドポイント接続成功！")
                print(f"投稿数: {len(posts)}件")
                
                if posts:
                    latest_post = posts[0]
                    print(f"最新投稿: {latest_post.get('title', {}).get('rendered', '不明')}")
                
                return True
            else:
                print(f"❌ 投稿エンドポイント接続失敗: HTTP {response.getcode()}")
                return False
                
    except Exception as e:
        print(f"❌ 投稿エンドポイントエラー: {e}")
        return False

if __name__ == "__main__":
    print("🚀 WordPress REST API テスト開始")
    print("=" * 50)
    
    # 基本接続テスト
    basic_success = test_wordpress_connection()
    
    if basic_success:
        # 投稿エンドポイントテスト
        posts_success = test_posts_endpoint()
        
        if posts_success:
            print("\n🎉 すべてのテストが成功しました！")
            print("システムの記事投稿準備が完了しています。")
        else:
            print("\n⚠️ 基本接続は成功しましたが、投稿エンドポイントに問題があります。")
    else:
        print("\n❌ WordPress接続に失敗しました。")
        print("設定を確認してください：")
        print("1. WordPressサイトのURL")
        print("2. ユーザー名")  
        print("3. アプリケーションパスワード")
        print("4. WordPress REST APIの有効性")
    
    print("\n" + "=" * 50)