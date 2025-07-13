#!/bin/bash

# 仮想通貨メディア自動記事生成システム セットアップスクリプト

set -e

echo "🚀 仮想通貨メディア自動記事生成システムのセットアップを開始します..."

# 必要なパッケージのインストール
echo "📦 必要なシステムパッケージを確認中..."

# Python仮想環境パッケージをインストール（必要に応じて）
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "python3-venv パッケージが必要です。以下のコマンドを実行してください:"
    echo "sudo apt update && sudo apt install python3.12-venv python3-pip"
    exit 1
fi

# 仮想環境の作成
echo "🐍 Python仮想環境を作成中..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 仮想環境を作成しました"
else
    echo "ℹ️ 仮想環境は既に存在します"
fi

# 仮想環境をアクティベート
echo "🔄 仮想環境をアクティベート中..."
source venv/bin/activate

# pipをアップグレード
echo "⬆️ pipをアップグレード中..."
pip install --upgrade pip

# 依存関係をインストール
echo "📚 依存関係をインストール中..."
pip install -r requirements.txt

# データベースディレクトリの作成
echo "🗄️ データベースディレクトリを作成中..."
mkdir -p data
mkdir -p logs

# 環境変数ファイルをコピー
echo "⚙️ 環境設定ファイルを準備中..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ .env ファイルを作成しました"
    echo "⚠️  .env ファイルを編集してAPIキーを設定してください"
else
    echo "ℹ️ .env ファイルは既に存在します"
fi

# データベースの初期化
echo "🏗️ データベースを初期化中..."
python3 -c "
from src.utils.config import Config
from src.database.db_manager import DatabaseManager
config = Config()
db_manager = DatabaseManager(config.DB_PATH)
print('データベース初期化完了')
"

# 接続テスト
echo "🔗 設定をテスト中..."
python3 -c "
from src.utils.config import Config
config = Config()
if config.validate_config():
    print('✅ 基本設定は有効です')
else:
    print('⚠️ 設定に問題があります。.envファイルを確認してください')
"

echo ""
echo "🎉 セットアップが完了しました！"
echo ""
echo "次のステップ:"
echo "1. .env ファイルを編集してAPIキーを設定"
echo "2. WordPress の設定を確認"
echo "3. 'python3 main.py' でシステムを開始"
echo ""
echo "仮想環境をアクティベートするには:"
echo "source venv/bin/activate"
echo ""
echo "詳細は README.md を参照してください。"