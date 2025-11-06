# 📚 書籍プロモーション動画生成システム

Google Veo 3.1を使って、書籍表紙画像から自動でプロモーション動画を生成するシステム。
機能とフォルダ構成のみ書いておきます。

## 🎯 主な機能

- **Google Veo 3.1**: 静止画から高品質な動画を生成
- **シンプルなAPI**: 1つのPythonファイルで動作

## 📁 プロジェクト構造

```
book-promo-veo-generator/
├── veo3_sample.py          # Veo 3.1サンプルコード（メイン）
├── requirements.txt        # 依存関係
├── .env.example            # 環境変数テンプレート
├── SPEC.md                 # 仕様書（全員が見る開発指針）
├── CLAUDE.md               # 開発原則（Fail-First等）
├── docs/
│   └── git-workflow.md     # Git運用フロー
└── output/                 # 生成動画の出力先
```
