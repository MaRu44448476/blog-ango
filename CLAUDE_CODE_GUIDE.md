# ClaudeCode環境での使用ガイド

## 🤖 ClaudeCode環境の特徴

このシステムはClaudeCode環境に最適化されており、以下の特徴があります：

- **OpenAI API不要**: Claudeの記事生成機能を活用
- **テンプレートベース**: 構造化されたテンプレートによる記事生成
- **手動実行**: 必要に応じて記事を生成・確認・投稿

## 🚀 セットアップと実行

### 1. 初期設定

```bash
# プロジェクトディレクトリに移動
cd crypto-media-system

# セットアップスクリプトを実行
./setup.sh
```

### 2. 環境変数の設定

`.env`ファイルを編集：

```bash
# WordPress設定（必須）
WP_URL=https://your-wordpress-site.com
WP_USERNAME=your_wordpress_username
WP_PASSWORD=your_wordpress_app_password

# 仮想通貨API（オプション）
COINGECKO_API_KEY=your_coingecko_api_key_here

# 記事生成設定
ARTICLE_MIN_LENGTH=500
ARTICLE_MAX_LENGTH=2000
MAX_ARTICLES_PER_DAY=5
```

**WordPress設定の詳細は `WORDPRESS_SETUP.md` を参照してください。**

### 3. システムテスト

```bash
# 仮想環境をアクティベート
source venv/bin/activate

# システム全体をテスト
python test_system.py
```

## 📝 記事生成の実行方法

### 手動での週刊まとめ記事生成

```bash
python -c "
from src.utils.config import Config
from src.database.db_manager import DatabaseManager
from src.collectors.api_client import CryptoAPIClient
from src.collectors.rss_parser import RSSParser
from src.generators.claude_generator import ClaudeGenerator

# 設定の読み込み
config = Config()
db_manager = DatabaseManager(config.DB_PATH)
api_client = CryptoAPIClient(config)
rss_parser = RSSParser(config)
generator = ClaudeGenerator(config)

print('📊 データ収集中...')
# ニュースデータ収集
news_data = rss_parser.collect_weekly_news()
print(f'ニュース: {len(news_data)}件')

# 市場データ収集
market_data = api_client.get_market_data()
print(f'市場データ: {len(market_data)}件')

# データベースに保存
db_manager.save_news_data(news_data)
db_manager.save_market_data(market_data)

print('✍️ 記事生成中...')
# 記事生成
article = generator.generate_weekly_summary(news_data, market_data)

if article:
    print(f'記事生成完了:')
    print(f'タイトル: {article[\"title\"]}')
    print(f'文字数: {article[\"word_count\"]}字')
    
    # 記事をデータベースに保存
    article_id = db_manager.save_article(article)
    print(f'記事ID: {article_id}で保存')
    
    # プレビュー表示
    print('\n--- 記事プレビュー ---')
    print(article['content'][:500] + '...')
    
    # 投稿確認
    confirm = input('\n📤 WordPressに投稿しますか？ (y/N): ')
    if confirm.lower() == 'y':
        from src.publishers.wordpress_client import WordPressClient
        wp_client = WordPressClient(config)
        result = wp_client.publish_article(article)
        
        if result and result.get('success'):
            print(f'✅ 投稿成功: {result.get(\"url\")}')
            db_manager.save_article(article, result)
        else:
            print(f'❌ 投稿失敗: {result.get(\"error_message\", \"不明なエラー\")}')
    else:
        print('投稿をキャンセルしました')
else:
    print('❌ 記事生成に失敗しました')
"
```

### 手動でのニュース記事生成

```bash
python -c "
from src.utils.config import Config
from src.collectors.rss_parser import RSSParser
from src.generators.claude_generator import ClaudeGenerator

config = Config()
rss_parser = RSSParser(config)
generator = ClaudeGenerator(config)

print('📰 最新ニュース取得中...')
news_items = rss_parser.collect_latest_news(hours=24)

if news_items:
    print(f'取得したニュース: {len(news_items)}件')
    
    # 重要度の高いニュースを表示
    top_news = sorted(news_items, key=lambda x: x.get('importance_score', 0), reverse=True)[:5]
    
    print('\n=== トップニュース ===')
    for i, news in enumerate(top_news, 1):
        print(f'{i}. {news.get(\"title\", \"\")} (重要度: {news.get(\"importance_score\", 0):.1f})')
    
    # 記事生成対象を選択
    try:
        choice = int(input('\n記事を生成するニュースの番号を選択 (1-5): ')) - 1
        if 0 <= choice < len(top_news):
            selected_news = top_news[choice]
            
            print(f'選択されたニュース: {selected_news.get(\"title\", \"\")}')
            print('✍️ 記事生成中...')
            
            article = generator.generate_news_article(selected_news)
            
            if article:
                print(f'記事生成完了:')
                print(f'タイトル: {article[\"title\"]}')
                print(f'文字数: {article[\"word_count\"]}字')
                print(f'カテゴリ: {article[\"category\"]}')
                
                # プレビュー表示
                print('\n--- 記事プレビュー ---')
                print(article['content'][:500] + '...')
                
                # 投稿確認
                confirm = input('\n📤 WordPressに投稿しますか？ (y/N): ')
                if confirm.lower() == 'y':
                    from src.publishers.wordpress_client import WordPressClient
                    from src.database.db_manager import DatabaseManager
                    
                    wp_client = WordPressClient(config)
                    db_manager = DatabaseManager(config.DB_PATH)
                    
                    result = wp_client.publish_article(article)
                    
                    if result and result.get('success'):
                        print(f'✅ 投稿成功: {result.get(\"url\")}')
                        db_manager.save_article(article, result)
                    else:
                        print(f'❌ 投稿失敗: {result.get(\"error_message\", \"不明なエラー\")}')
                else:
                    print('投稿をキャンセルしました')
            else:
                print('❌ 記事生成に失敗しました')
        else:
            print('無効な選択です')
    except ValueError:
        print('無効な入力です')
else:
    print('ニュースが取得できませんでした')
"
```

## 🎯 ClaudeCodeでの記事品質向上

### 1. 記事内容の手動確認・編集

```bash
python -c "
# 生成された記事を確認
from src.database.db_manager import DatabaseManager
from src.utils.config import Config

config = Config()
db_manager = DatabaseManager(config.DB_PATH)

# 最新の記事を取得
import sqlite3
with sqlite3.connect(config.DB_PATH) as conn:
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM generated_articles ORDER BY generation_date DESC LIMIT 5')
    articles = cursor.fetchall()
    
    print('=== 最近生成された記事 ===')
    for i, article in enumerate(articles):
        print(f'{i+1}. ID: {article[0]} | {article[1]} | {article[6]}字')
"
```

### 2. 記事の編集とカスタマイズ

記事生成後、ClaudeCodeの機能を使って記事を改善できます：

```python
# 記事の改善例
def improve_article_with_claude(article_content):
    """
    ClaudeCodeでこの関数を呼び出し、記事内容を改善
    """
    improved_prompt = f"""
以下の仮想通貨記事をより魅力的で読みやすく改善してください：

【現在の記事】
{article_content}

【改善要件】
1. より自然な日本語表現に修正
2. 読者にとって分かりやすい構成に変更
3. 重要なポイントを強調
4. SEOを意識したキーワードの配置
5. 文字数は1500-2000字を目安

改善された記事を出力してください。
    """
    
    # ClaudeCodeでこのプロンプトを実行
    return improved_prompt
```

### 3. WordPress投稿前のプレビュー

```bash
python -c "
# 記事のHTMLプレビューを生成
def preview_article(article_id):
    from src.database.db_manager import DatabaseManager
    from src.utils.config import Config
    import sqlite3
    
    config = Config()
    
    with sqlite3.connect(config.DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT title, content FROM generated_articles WHERE id = ?', (article_id,))
        result = cursor.fetchone()
        
        if result:
            title, content = result
            html_preview = f'''
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h2 {{ color: #2c3e50; }}
        h3 {{ color: #3498db; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {content}
</body>
</html>
            '''
            
            # プレビューファイルを保存
            with open(f'preview_article_{article_id}.html', 'w', encoding='utf-8') as f:
                f.write(html_preview)
            
            print(f'プレビューファイルを生成: preview_article_{article_id}.html')
            return html_preview
        else:
            print('記事が見つかりません')
            return None

# 使用例
# preview_article(1)  # 記事ID 1 のプレビューを生成
"
```

## 📊 統計とモニタリング

### 日次レポートの生成

```bash
python -c "
from src.database.db_manager import DatabaseManager
from src.utils.config import Config
from datetime import datetime

config = Config()
db_manager = DatabaseManager(config.DB_PATH)

stats = db_manager.get_daily_stats()

print(f'=== {datetime.now().strftime(\"%Y年%m月%d日\")} の統計 ===')
print(f'📰 収集ニュース: {stats.get(\"news_collected_today\", 0)}件')
print(f'✍️ 生成記事: {stats.get(\"articles_generated_today\", 0)}件')
print(f'📤 投稿記事: {stats.get(\"articles_published_today\", 0)}件')
print(f'🔌 API使用状況: {stats.get(\"api_usage_today\", {})}')
"
```

## 🔧 カスタマイズ例

### 記事生成の設定調整

```bash
# .envファイルで記事生成をカスタマイズ
ARTICLE_MIN_LENGTH=800          # 最小文字数を800字に
ARTICLE_MAX_LENGTH=1500         # 最大文字数を1500字に
MAX_ARTICLES_PER_DAY=3          # 1日最大3記事まで

# RSS取得の設定
RSS_FEEDS_ADDITIONAL=https://additional-crypto-news.com/rss
```

### 新しい記事テンプレートの追加

```python
# templates/custom_template.txt
def create_custom_article_template():
    return """
<h2>仮想通貨ニュース速報</h2>
<p>{summary}</p>

<h2>ポイント解説</h2>
<ul>
<li>{point1}</li>
<li>{point2}</li>
<li>{point3}</li>
</ul>

<h2>市場への影響</h2>
<p>{market_impact}</p>

<h2>投資家への示唆</h2>
<p>{investment_insight}</p>
    """
```

## 💡 ベストプラクティス

### 1. 記事生成の品質管理

- **段階的確認**: 生成→プレビュー→編集→投稿の流れ
- **手動チェック**: 投稿前に必ず内容を確認
- **カテゴリ統一**: WordPress側でカテゴリを事前に整理

### 2. 効率的な運用

```bash
# 毎日の運用ルーチン例
echo "=== 仮想通貨メディアシステム 日次運用 ==="

# 1. データ収集確認
python -c "from src.collectors.rss_parser import RSSParser; from src.utils.config import Config; rss = RSSParser(Config()); print(f'ニュース収集: {len(rss.collect_latest_news())}件')"

# 2. 重要ニュースの確認
python -c "from src.collectors.rss_parser import RSSParser; from src.utils.config import Config; rss = RSSParser(Config()); news = rss.get_top_stories(5); [print(f'{i+1}. {n.get(\"title\", \"\")}') for i, n in enumerate(news)]"

# 3. 市場データ確認
python -c "from src.collectors.api_client import CryptoAPIClient; from src.utils.config import Config; api = CryptoAPIClient(Config()); data = api.get_market_data()[:5]; [print(f'{d.get(\"symbol\")}: ${d.get(\"price\", 0):,.2f} ({d.get(\"price_change_percentage_24h\", 0):+.1f}%)') for d in data]"
```

### 3. トラブル時の対応

```bash
# ログの確認
tail -50 logs/crypto_media.log

# データベースの状態確認
python -c "from src.database.db_manager import DatabaseManager; from src.utils.config import Config; db = DatabaseManager(Config().DB_PATH); print(db.get_daily_stats())"

# WordPress接続確認
python -c "from src.publishers.wordpress_client import WordPressClient; from src.utils.config import Config; wp = WordPressClient(Config()); print('接続OK' if wp.test_connection() else '接続NG')"
```

ClaudeCode環境では、このような手動実行とプレビュー機能を活用して、高品質な記事を安定的に生成・投稿できます！