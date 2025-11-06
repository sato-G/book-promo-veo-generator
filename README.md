# 📚 書籍プロモーション動画生成システム

Google Veo 3.1を使って、書籍表紙画像から自動でプロモーション動画を生成するシステム。

## 🎯 主な機能

- **Google Veo 3.1**: 静止画から高品質な動画を生成
- **シンプルなAPI**: 1つのPythonファイルで動作

## 🚀 クイックスタート

### 1. インストール

```bash
# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
```

### 2. 認証設定

```bash
# 環境変数設定
export GOOGLE_API_KEY=your_api_key_here
```

### 3. 動画生成

```bash
# サンプル実行
python veo3_sample.py \
  --image path/to/book_cover.png \
  --prompt "本のタイトルが浮かび上がる" \
  --duration 8
```

## 📁 プロジェクト構造

```
book-promo-veo-generator/
├── veo3_sample.py          # Veo 3.1サンプルコード（メイン）
├── requirements.txt        # 依存関係
├── .env.example            # 環境変数テンプレート
├── SPEC.md                 # 仕様書（全員が見る開発指針）
├── CLAUDE.md               # 開発原則（Fail-First等）
├── docs/                   # ドキュメント
│   ├── architecture.md     # システムアーキテクチャ
│   └── git-workflow.md     # Git運用フロー
└── output/                 # 生成動画の出力先
```

## 📚 ドキュメント

### 開発者向け
- **[SPEC.md](SPEC.md)** - プロジェクト仕様書（全員が見る開発指針）
- **[CLAUDE.md](CLAUDE.md)** - 開発原則（Fail-First原則等）
- **[docs/architecture.md](docs/architecture.md)** - システムアーキテクチャ
- **[docs/git-workflow.md](docs/git-workflow.md)** - Git運用フロー

## 🌳 Git戦略（Git Flow）

本プロジェクトは**Git Flow**を採用：

- **master**: プロダクション用（常に動作する）
- **develop**: 開発統合ブランチ
- **feature/***: 機能開発ブランチ

詳細は[Git運用フロー](docs/git-workflow.md)を参照。
