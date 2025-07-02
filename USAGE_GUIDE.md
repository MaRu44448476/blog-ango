# 使用ガイド

## 🚀 セットアップから運用まで

### 1. 初期セットアップ

```bash
# 1. セットアップスクリプトを実行
./setup.sh

# 2. .envファイルを編集してAPIキーを設定
nano .env
```

### 2. 必要なAPIキーの取得

#### OpenAI API（必須）
1. [OpenAI Platform](https://platform.openai.com/)にアクセス
2. アカウントを作成しAPIキーを生成
3. `.env`ファイルの`OPENAI_API_KEY`に設定

#### WordPress設定（必須）
1. WordPressの管理画面 → ユーザー → プロフィール
2. アプリケーションパスワードを生成
3. `.env`ファイルに設定：
   ```
   WP_URL=https://your-site.com
   WP_USERNAME=your_username
   WP_PASSWORD=generated_app_password
   ```

#### 仮想通貨API（オプション）
- **CoinGecko**: [Pro API](https://www.coingecko.com/en/api)（無料版も利用可能）
- **CoinMarketCap**: [API](https://coinmarketcap.com/api/)

### 3. システムテスト

```bash
# システム全体をテスト
python test_system.py
```

### 4. 手動実行

```bash
# 仮想環境をアクティベート
source venv/bin/activate

# 週刊まとめ記事を生成
python -c "
from main import generate_weekly_summary
generate_weekly_summary()
"

# 日次ニュース記事を生成
python -c "
from main import generate_daily_news
generate_daily_news()
"
```

### 5. 自動実行（推奨）

```bash
# メインスクリプトを実行（スケジューラー付き）
python main.py
```

## 📊 運用モニタリング

### 日次統計の確認

```bash
python -c "
from src.database.db_manager import DatabaseManager
from src.utils.config import Config

config = Config()
db = DatabaseManager(config.DB_PATH)
stats = db.get_daily_stats()

print('=== 今日の統計 ===')
print(f'収集ニュース: {stats.get(\"news_collected_today\", 0)}件')
print(f'生成記事: {stats.get(\"articles_generated_today\", 0)}件')
print(f'投稿記事: {stats.get(\"articles_published_today\", 0)}件')
print(f'API使用状況: {stats.get(\"api_usage_today\", {})}')
"
```

### ログの確認

```bash
# リアルタイムログ監視
tail -f logs/crypto_media.log

# エラーログのみ表示
grep ERROR logs/crypto_media.log

# 今日のログを表示
grep $(date +%Y-%m-%d) logs/crypto_media.log
```

## 🔧 カスタマイズ例

### 記事生成頻度の変更

`main.py`のスケジュール設定を編集：

```python
# 毎日12時に週刊まとめを生成
schedule.every().day.at("12:00").do(generate_weekly_summary)

# 3時間ごとにニュース記事を生成
schedule.every(3).hours.do(generate_daily_news)
```

### 新しいニュースソースの追加

`.env`ファイルに追加：

```bash
RSS_FEEDS_NEWSITE=https://newsite.com/rss
```

`src/utils/config.py`の`RSS_FEEDS`プロパティを更新：

```python
@property
def RSS_FEEDS(self) -> Dict[str, str]:
    return {
        "coindesk": os.getenv("RSS_FEEDS_COINDESK", "..."),
        "cointelegraph": os.getenv("RSS_FEEDS_COINTELEGRAPH", "..."),
        "newsite": os.getenv("RSS_FEEDS_NEWSITE", "https://newsite.com/rss")
    }
```

### 記事の品質設定

`src/utils/config.py`で文字数制限を調整：

```python
@property
def ARTICLE_MIN_LENGTH(self) -> int:
    return int(os.getenv("ARTICLE_MIN_LENGTH", "300"))  # 最小300字

@property
def ARTICLE_MAX_LENGTH(self) -> int:
    return int(os.getenv("ARTICLE_MAX_LENGTH", "1500"))  # 最大1500字
```

## 🚨 トラブルシューティング

### よくある問題と解決方法

#### 1. OpenAI API制限エラー

```
ERROR - OpenAI API記事生成エラー: Rate limit exceeded
```

**解決方法**:
- `.env`で`OPENAI_RATE_LIMIT`を下げる（デフォルト: 20）
- OpenAIの使用量プランを確認

#### 2. WordPress投稿エラー

```
ERROR - WordPress認証エラー
```

**解決方法**:
- アプリケーションパスワードを再生成
- WordPress REST APIが有効か確認
- URLが正しいか確認（https://site.com 末尾のスラッシュなし）

#### 3. データベースエラー

```
ERROR - データベース初期化エラー
```

**解決方法**:
- `data/`ディレクトリの権限を確認
- ディスク容量を確認
- SQLiteがインストールされているか確認

#### 4. RSS取得エラー

```
WARNING - フィード取得エラー
```

**解決方法**:
- インターネット接続を確認
- RSS URLが有効か確認
- User-Agentがブロックされていないか確認

### デバッグモード

詳細なログでシステムを実行：

```bash
# 環境変数でログレベルを設定
export LOG_LEVEL=DEBUG
python main.py
```

または`.env`ファイルで設定：

```bash
LOG_LEVEL=DEBUG
```

## 📈 パフォーマンス最適化

### API制限の管理

```bash
# .envファイルで調整
API_RATE_LIMIT=30          # APIリクエスト制限（毎分）
OPENAI_RATE_LIMIT=10       # OpenAI制限（毎分）
MAX_ARTICLES_PER_DAY=20    # 1日の最大記事数
```

### データベースの最適化

```python
# 古いデータを定期的にクリーンアップ
python -c "
from src.database.db_manager import DatabaseManager
from src.utils.config import Config

config = Config()
db = DatabaseManager(config.DB_PATH)
db.cleanup_old_data(days=30)  # 30日以前のデータを削除
print('データベースクリーンアップ完了')
"
```

## 🔄 本番環境での運用

### systemdサービスとして実行

```bash
# サービスファイルを作成
sudo nano /etc/systemd/system/crypto-media.service
```

サービスファイルの内容：

```ini
[Unit]
Description=Crypto Media System
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/crypto-media-system
ExecStart=/path/to/crypto-media-system/venv/bin/python main.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

サービスを有効化：

```bash
sudo systemctl daemon-reload
sudo systemctl enable crypto-media
sudo systemctl start crypto-media
sudo systemctl status crypto-media
```

### バックアップ設定

```bash
# データベースの日次バックアップ
crontab -e

# 以下を追加
0 2 * * * cp /path/to/crypto-media-system/data/crypto_media.db /path/to/backup/crypto_media_$(date +\%Y\%m\%d).db
```

## 📞 サポート情報

システムに関する質問や問題が発生した場合：

1. **まず確認**: ログファイル`logs/crypto_media.log`をチェック
2. **テスト実行**: `python test_system.py`で各コンポーネントをテスト
3. **設定確認**: `.env`ファイルの設定を再確認
4. **バージョン確認**: 依存関係を最新に更新 `pip install -r requirements.txt --upgrade`

## 🎯 次のステップ

システムが正常に動作したら：

1. **記事品質の向上**: プロンプトの調整
2. **新機能の追加**: SNS投稿、画像生成など
3. **監視の強化**: アラート設定、ダッシュボード作成
4. **スケーリング**: 複数サイトでの運用