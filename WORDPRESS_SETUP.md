# WordPress REST API設定ガイド

## 📋 概要

このシステムはWordPress REST APIを使用して記事を自動投稿します。以下の手順でWordPressサイトを設定してください。

## 🔧 WordPress側の設定

### 1. WordPress REST APIの有効化確認

WordPress 4.7以降では、REST APIはデフォルトで有効になっています。

**確認方法:**
ブラウザで以下のURLにアクセス:
```
https://your-site.com/wp-json/wp/v2/posts
```

JSONレスポンスが返されれば、REST APIは正常に動作しています。

### 2. アプリケーションパスワードの設定

#### 手順1: WordPressにログイン
WordPressの管理画面にログインします。

#### 手順2: ユーザープロフィールを開く
- 管理画面 → **ユーザー** → **プロフィール**
- または管理画面 → **ユーザー** → **すべてのユーザー** → 対象ユーザーを編集

#### 手順3: アプリケーションパスワードを生成
ページ下部の「**アプリケーションパスワード**」セクションで：

1. **新しいアプリケーションパスワード名**に「CryptoMediaSystem」など任意の名前を入力
2. **新しいアプリケーションパスワードを追加**ボタンをクリック
3. **生成されたパスワードをコピー**（このパスワードは一度しか表示されません）

例: `1234 5678 9012 3456 7890 abcd`

#### 手順4: .envファイルに設定
```bash
WP_URL=https://your-wordpress-site.com
WP_USERNAME=your_wordpress_username
WP_PASSWORD=1234 5678 9012 3456 7890 abcd
```

**重要**: 
- `WP_PASSWORD`には通常のログインパスワードではなく、生成されたアプリケーションパスワードを使用
- スペースは含めて設定してください

### 3. 権限の確認

投稿用ユーザーに以下の権限が必要です：
- **投稿の作成・編集権限**（編集者以上の権限）
- **カテゴリ・タグの作成権限**

## 🧪 接続テスト

### 基本的な接続テスト

```bash
cd crypto-media-system
source venv/bin/activate
python -c "
from src.publishers.wordpress_client import WordPressClient
from src.utils.config import Config

config = Config()
wp_client = WordPressClient(config)

if wp_client.test_connection():
    print('✅ WordPress接続成功')
else:
    print('❌ WordPress接続失敗')
"
```

### 詳細テスト

```bash
python -c "
from src.publishers.wordpress_client import WordPressClient
from src.utils.config import Config

config = Config()
wp_client = WordPressClient(config)

# サイト情報取得
site_info = wp_client._make_request('GET', '')
if site_info:
    print(f'サイト名: {site_info.get(\"name\", \"不明\")}')
    print(f'説明: {site_info.get(\"description\", \"不明\")}')
    print(f'URL: {site_info.get(\"url\", \"不明\")}')

# 最近の投稿を取得
recent_posts = wp_client.get_recent_posts(limit=3)
print(f'最近の投稿: {len(recent_posts)}件')
"
```

## 🔒 セキュリティ設定

### 1. HTTPS必須

WordPress REST APIはHTTPS環境での使用を強く推奨します：
```bash
WP_URL=https://your-site.com  # HTTPSを使用
```

### 2. アプリケーションパスワードの管理

- **定期的な更新**: 3-6ヶ月ごとにパスワードを更新
- **最小権限の原則**: 必要最小限の権限のみを付与
- **使用後の削除**: 不要になったアプリケーションパスワードは削除

### 3. アクセス制限（オプション）

特定のIPアドレスからのみアクセスを許可する場合：

**.htaccessに追加:**
```apache
# WordPress REST API アクセス制限
<Files "wp-json">
    Order Deny,Allow
    Deny from all
    Allow from YOUR_SERVER_IP
</Files>
```

## 🚨 トラブルシューティング

### よくあるエラーと解決方法

#### 1. 401 Unauthorized
```
ERROR - WordPress認証エラー: ユーザー名/パスワードを確認してください
```

**原因と解決策:**
- アプリケーションパスワードが間違っている → 再生成
- ユーザー名が間違っている → 確認・修正
- WordPress 5.6未満 → WordPressをアップデート

#### 2. 403 Forbidden
```
ERROR - WordPress権限エラー: 投稿権限がありません
```

**原因と解決策:**
- ユーザーに投稿権限がない → 編集者以上の権限を付与
- プラグインによるアクセス制限 → セキュリティプラグインの設定確認

#### 3. 404 Not Found
```
ERROR - WordPress APIエンドポイントが見つかりません
```

**原因と解決策:**
- URLが間違っている → .envのWP_URLを確認
- パーマリンク設定の問題 → WordPress管理画面でパーマリンクを再保存
- REST APIが無効 → プラグインで無効化されていないか確認

#### 4. SSL/TLS エラー
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**原因と解決策:**
- SSL証明書の問題 → 有効なSSL証明書を設定
- 自己署名証明書 → 本番環境では有効な証明書を使用

### デバッグ手順

#### 1. 手動でREST APIを確認
```bash
curl -X GET "https://your-site.com/wp-json/wp/v2/posts" \
  -H "Authorization: Basic $(echo -n 'username:app_password' | base64)"
```

#### 2. 詳細ログの有効化
```bash
# .envファイル
LOG_LEVEL=DEBUG
```

#### 3. WordPressのデバッグモード
```php
// wp-config.php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
```

## 📝 テスト投稿の実行

設定が完了したら、テスト投稿を実行してみましょう：

```bash
python -c "
from src.publishers.wordpress_client import WordPressClient
from src.utils.config import Config
from datetime import datetime

config = Config()
wp_client = WordPressClient(config)

# テスト記事データ
test_article = {
    'title': 'テスト投稿 - 仮想通貨メディアシステム',
    'content': '''
<h2>システムテスト</h2>
<p>これは仮想通貨メディア自動記事生成システムからのテスト投稿です。</p>
<p>投稿日時: ''' + datetime.now().strftime('%Y年%m月%d日 %H:%M') + '''</p>
<p><small>このテスト投稿は削除しても構いません。</small></p>
    ''',
    'article_type': 'test',
    'category': 'テスト',
    'tags': ['テスト', 'システム確認'],
    'word_count': 100
}

# 投稿実行
result = wp_client.publish_article(test_article)

if result and result.get('success'):
    print(f'✅ テスト投稿成功!')
    print(f'投稿ID: {result.get(\"id\")}')
    print(f'URL: {result.get(\"url\")}')
else:
    print('❌ テスト投稿失敗')
    print(f'エラー: {result.get(\"error_message\", \"不明なエラー\")}')
"
```

## 🔧 高度な設定

### カスタムフィールドの使用

記事にメタデータを保存したい場合：

```php
// functions.php に追加
function add_crypto_meta_fields() {
    register_rest_field('post', 'crypto_article_type', array(
        'get_callback' => function($post) {
            return get_post_meta($post['id'], 'crypto_article_type', true);
        },
        'update_callback' => function($value, $post) {
            update_post_meta($post->ID, 'crypto_article_type', $value);
        }
    ));
}
add_action('rest_api_init', 'add_crypto_meta_fields');
```

### Webhookの設定

記事投稿時に外部システムに通知する場合：

```php
// functions.php に追加
function notify_on_crypto_post($post_id, $post, $update) {
    if ($post->post_type !== 'post' || $update) return;
    
    $meta = get_post_meta($post_id, 'crypto_article_type', true);
    if ($meta) {
        // 外部システムに通知
        wp_remote_post('https://your-external-system.com/webhook', array(
            'body' => json_encode(array(
                'post_id' => $post_id,
                'title' => $post->post_title,
                'type' => $meta
            ))
        ));
    }
}
add_action('wp_insert_post', 'notify_on_crypto_post', 10, 3);
```

これで、ClaudeCode環境での記事生成とWordPress REST APIの設定が完了です！