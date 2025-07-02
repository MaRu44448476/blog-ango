#!/usr/bin/env python3
"""
クイック記事生成・投稿テスト
"""

import base64
import json
import urllib.request
import urllib.parse
from datetime import datetime

# WordPress設定
WP_URL = "https://crypto-dictionary.net"
WP_USERNAME = "MaRu"
WP_PASSWORD = "3sMS 8JWd xS8k OkOZ qhX2 3u4z"

def create_test_article():
    """テスト記事を作成"""
    now = datetime.now()
    
    title = f"【テスト投稿】仮想通貨自動記事生成システム - {now.strftime('%Y年%m月%d日 %H:%M')}"
    
    content = f"""
<h2>システムテスト投稿</h2>
<p>これは仮想通貨メディア自動記事生成システムからのテスト投稿です。</p>

<h2>システム情報</h2>
<ul>
<li><strong>投稿日時</strong>: {now.strftime('%Y年%m月%d日 %H時%M分')}</li>
<li><strong>システム</strong>: ClaudeCode環境</li>
<li><strong>記事生成</strong>: テンプレートベース</li>
<li><strong>投稿方法</strong>: WordPress REST API</li>
</ul>

<h2>今後の機能</h2>
<p>本システムでは以下の記事を自動生成予定です：</p>
<ul>
<li>週刊仮想通貨ニュースまとめ</li>
<li>重要ニュースの速報記事</li>
<li>市場分析レポート</li>
<li>仮想通貨解説記事</li>
</ul>

<h2>注意事項</h2>
<p><small>このテスト投稿は削除しても構いません。システムが正常に動作していることを確認するためのものです。</small></p>

<hr>
<p><small>※本記事はシステムテスト目的で自動生成されました。</small></p>
    """
    
    return {
        'title': title,
        'content': content,
        'status': 'publish',  # 即座に公開
        'categories': [],  # カテゴリなし（後で手動設定可能）
        'tags': []  # タグなし
    }

def publish_test_article():
    """テスト記事をWordPressに投稿"""
    
    # 認証ヘッダー
    credentials = f"{WP_USERNAME}:{WP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode()
    
    headers = {
        'Authorization': f'Basic {token}',
        'Content-Type': 'application/json',
        'User-Agent': 'CryptoMediaSystem/1.0'
    }
    
    # 投稿データ
    article = create_test_article()
    post_data = json.dumps(article).encode('utf-8')
    
    # 投稿URL
    posts_url = f"{WP_URL}/wp-json/wp/v2/posts"
    
    print("📝 テスト記事投稿中...")
    print(f"タイトル: {article['title']}")
    
    try:
        request = urllib.request.Request(posts_url, data=post_data, headers=headers, method='POST')
        
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.getcode() in [200, 201]:
                result = json.loads(response.read().decode())
                
                print("✅ テスト記事投稿成功！")
                print(f"投稿ID: {result.get('id')}")
                print(f"投稿URL: {result.get('link')}")
                print(f"ステータス: {result.get('status')}")
                print(f"公開日: {result.get('date')}")
                
                return result
            else:
                print(f"❌ 投稿失敗: HTTP {response.getcode()}")
                return None
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP エラー: {e.code}")
        error_detail = e.read().decode() if hasattr(e, 'read') else 'なし'
        print(f"エラー詳細: {error_detail}")
        return None
        
    except Exception as e:
        print(f"❌ 投稿エラー: {e}")
        return None

def main():
    """メイン実行"""
    print("🚀 仮想通貨メディアシステム - テスト記事投稿")
    print("=" * 60)
    
    # 投稿確認
    confirm = input("テスト記事をWordPressに投稿しますか？ (y/N): ")
    
    if confirm.lower() == 'y':
        result = publish_test_article()
        
        if result:
            print("\n🎉 テスト投稿が完了しました！")
            print(f"記事を確認: {result.get('link')}")
            print("\n次のステップ:")
            print("1. WordPressダッシュボードで記事を確認")
            print("2. 必要に応じてカテゴリー・タグを設定")
            print("3. 本格的な記事生成を開始")
        else:
            print("\n❌ テスト投稿に失敗しました")
            print("設定やWordPressの状態を確認してください")
    else:
        print("テスト投稿をキャンセルしました")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()