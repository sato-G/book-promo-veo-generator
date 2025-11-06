# 書籍プロモーション動画生成システム - 仕様書

**バージョン**: 1.0
**最終更新**: 2025-11-06
**ステータス**: Active

---

## 📋 現在のタスク

### Phase 1: Streamlit UI統合（進行中）

**目標**: veo3_sample.pyをStreamlitから動かせるようにする

**タスク**:
- [x] Streamlit UIファイル作成（`app.py`）
- [x] veo3_sample.pyを関数として呼び出せるように調整
- [x] 画像アップロード機能
- [x] プロンプト入力フォーム
- [x] 動画生成ボタン
- [x] 生成された動画のプレビュー・ダウンロード

**技術要件**:
- Streamlitでファイルアップロード（`st.file_uploader`）
- 環境変数読み込み（`python-dotenv`）
- 進捗表示（`st.progress`, `st.spinner`）

**成功基準**:
- StreamlitからVeo 3.1で動画生成できる
- 生成された動画をブラウザでプレビューできる

---
