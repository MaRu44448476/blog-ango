# 仮想通貨メディア自動記事生成システム

![Python](https://img.shields.io/badge/python-v3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

仮想通貨に関する情報を自動収集し、WordPress用の記事を自動生成・投稿するPythonベースのシステムです。

## 📋 概要

このシステムは以下の機能を提供します：

- **情報収集**: CoinGecko、CoinMarketCap等のAPIから価格データを取得
- **ニュース収集**: 主要仮想通貨ニュースサイトからRSSフィードを取得
- **記事生成**: OpenAI APIを使用して4種類の記事を自動生成
- **WordPress投稿**: REST APIを使用した自動投稿
- **スケジューリング**: 定期的な記事生成と投稿

## 🚀 クイックスタート

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd crypto-media-system
```

### 2. システムのセットアップ

```bash
chmod +x setup.sh
./setup.sh
```

### 3. 環境変数の設定

`.env` ファイルを編集して必要なAPIキーを設定：

```bash
# API Keys
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here
COINGECKO_API_KEY=your_coingecko_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# WordPress設定
WP_URL=https://your-wordpress-site.com
WP_USERNAME=your_wordpress_username
WP_PASSWORD=your_wordpress_app_password
```

### 4. システムの起動

```bash
source venv/bin/activate
python main.py
```

## 📁 ディレクトリ構造

```
crypto-media-system/
├── src/
│   ├── collectors/          # データ収集モジュール
│   │   ├── api_client.py    # 仮想通貨APIクライアント
│   │   └── rss_parser.py    # RSSパーサー
│   ├── generators/          # コンテンツ生成モジュール
│   │   ├── weekly_summary.py # 週刊まとめ記事生成
│   │   └── news_writer.py   # ニュース記事生成
│   ├── publishers/          # WordPress投稿モジュール
│   │   └── wordpress_client.py
│   ├── database/           # データベース管理
│   │   └── db_manager.py
│   └── utils/              # ユーティリティ
│       └── config.py       # 設定管理
├── templates/              # 記事テンプレート
├── data/                   # データベースファイル
├── logs/                   # ログファイル
├── .env                    # 環境変数
├── requirements.txt        # 依存関係
├── setup.sh               # セットアップスクリプト
└── main.py                # メインスクリプト
```

## 🛠 主要機能

### 1. データ収集

#### 仮想通貨価格データ
- **CoinGecko**: 無料APIで主要通貨の価格データを取得
- **CoinMarketCap**: 詳細な市場データと統計情報
- **CryptoCompare**: 追加の市場データとトレンド情報

#### ニュースデータ
- **RSS フィード**: CoinDesk、CoinTelegraph、Decrypt等
- **重要度スコア**: 自動的にニュースの重要度を評価
- **カテゴリ分類**: 市場、技術、規制等のカテゴリ別分類

### 2. 記事生成

#### 週刊ニュースまとめ
- 過去1週間の重要ニュースを5-7個選定
- 各ニュースに200-300字の要約
- 市場動向の分析を含める

```python
from src.generators.weekly_summary import WeeklySummaryGenerator

generator = WeeklySummaryGenerator(config)
article = generator.generate_summary(news_data, market_data)
```

#### 速報ニュース
- 重要なニュースを検知して短い記事を生成
- 500-800字程度
- 緊急度に応じた自動投稿

```python
from src.generators.news_writer import NewsWriter

writer = NewsWriter(config)
article = writer.generate_breaking_news(news_item)
```

### 3. WordPress連携

#### 自動投稿機能
- WordPress REST APIを使用
- カテゴリー・タグの自動設定
- メタデータの保存

```python
from src.publishers.wordpress_client import WordPressClient

wp_client = WordPressClient(config)
result = wp_client.publish_article(article)
```

## ⚙️ 設定

### 環境変数

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI APIキー | ✅ |
| `WP_URL` | WordPress サイトURL | ✅ |
| `WP_USERNAME` | WordPress ユーザー名 | ✅ |
| `WP_PASSWORD` | WordPress アプリパスワード | ✅ |
| `COINMARKETCAP_API_KEY` | CoinMarketCap APIキー | - |
| `COINGECKO_API_KEY` | CoinGecko APIキー | - |

### スケジュール設定

デフォルトのスケジュール：
- **週刊まとめ**: 毎週月曜日 09:00
- **日次ニュース**: 毎日 10:00

カスタマイズは `.env` ファイルで設定可能：

```bash
WEEKLY_SUMMARY_DAY=Monday
WEEKLY_SUMMARY_TIME=09:00
DAILY_NEWS_TIME=10:00
```

## 📊 データベース

SQLiteデータベースで以下のデータを管理：

- **news_data**: 収集したニュース
- **market_data**: 仮想通貨市場データ
- **generated_articles**: 生成した記事
- **publish_history**: 投稿履歴
- **api_usage**: API使用状況

### データベースの管理

```python
from src.database.db_manager import DatabaseManager

db_manager = DatabaseManager("data/crypto_media.db")

# 統計の取得
stats = db_manager.get_daily_stats()

# 古いデータのクリーンアップ
db_manager.cleanup_old_data(days=30)
```

## 🔍 監視とログ

### ログレベル

- `INFO`: 一般的な動作ログ
- `WARNING`: 注意が必要な状況
- `ERROR`: エラー情報
- `DEBUG`: デバッグ情報

### ログファイル

```bash
tail -f logs/crypto_media.log
```

### 統計ダッシュボード

```python
# 日次統計の確認
python -c "
from src.database.db_manager import DatabaseManager
from src.utils.config import Config

config = Config()
db = DatabaseManager(config.DB_PATH)
stats = db.get_daily_stats()
print(f'今日収集したニュース: {stats[\"news_collected_today\"]}件')
print(f'今日生成した記事: {stats[\"articles_generated_today\"]}件')
print(f'今日投稿した記事: {stats[\"articles_published_today\"]}件')
"
```

## 🧪 テストとトラブルシューティング

### 接続テスト

```python
from src.utils.config import Config
from src.publishers.wordpress_client import WordPressClient

config = Config()
wp_client = WordPressClient(config)

if wp_client.test_connection():
    print("WordPress接続成功")
else:
    print("WordPress接続失敗")
```

### APIテスト

```python
from src.collectors.api_client import CryptoAPIClient

api_client = CryptoAPIClient(config)
market_data = api_client.get_market_data()
print(f"取得したデータ数: {len(market_data)}")
```

### よくある問題

1. **WordPress認証エラー**
   - アプリケーションパスワードが正しく設定されているか確認
   - WordPress REST APIが有効になっているか確認

2. **OpenAI API制限**
   - API使用量を確認
   - レート制限の設定を調整

3. **データベースエラー**
   - データベースファイルの権限を確認
   - ディスク容量を確認

## 🔧 カスタマイズ

### 新しい記事タイプの追加

1. `src/generators/` に新しいジェネレータクラスを作成
2. `main.py` でスケジューリングを設定
3. `templates/` にテンプレートファイルを追加

### 新しいデータソースの追加

1. `src/collectors/` に新しいコレクタークラスを作成
2. データベーススキーマを更新（必要に応じて）
3. 設定ファイルにAPI設定を追加

## 📈 パフォーマンス最適化

### レート制限の管理

```python
# config.py での設定
API_RATE_LIMIT=60  # 1分間のリクエスト数
OPENAI_RATE_LIMIT=20  # OpenAI API制限
```

### バッチ処理

```python
# 複数記事の一括生成
articles = news_writer.batch_generate_news(news_items, max_articles=5)

# 複数記事の一括投稿
results = wp_client.batch_publish_articles(articles)
```

## 🚀 本番環境での運用

### systemdサービスの設定

```bash
# /etc/systemd/system/crypto-media.service
[Unit]
Description=Crypto Media System
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/crypto-media-system
ExecStart=/path/to/crypto-media-system/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### cronでの定期実行

```bash
# crontabに追加
0 9 * * 1 cd /path/to/crypto-media-system && ./venv/bin/python main.py --weekly-summary
0 10 * * * cd /path/to/crypto-media-system && ./venv/bin/python main.py --daily-news
```

## 🔒 セキュリティ

- APIキーは環境変数で管理
- WordPress はアプリケーションパスワードを使用
- ログにセンシティブ情報を含めない
- 定期的なバックアップの実装

## 📝 ライセンス

MIT License

## 🤝 コントリビュート

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add some amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. 依存関係が正しくインストールされているか
2. 環境変数が正しく設定されているか
3. ログファイルでエラー詳細を確認

---

**注意**: このシステムは情報提供を目的としており、投資助言ではありません。投資判断は自己責任でお願いします。