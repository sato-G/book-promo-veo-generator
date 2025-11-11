# 書籍プロモーション動画生成システム - 仕様書

**バージョン**: 4.0
**最終更新**: 2025-11-12
**ステータス**: Active

---

## 📋 現在のタスク

### Phase 3: アニメーション強化とUI改善

**目標**:
- スライドショー動画のクオリティ向上
- 視覚的インパクトの強化
- プロフェッショナルな仕上がり

**タスク:**

#### Phase 3-A: 冒頭アニメーション
- ショート動画の冒頭にインパクトのあるアニメーションを追加
- 拡大された画像 → 元サイズにズームバック
- 字幕付きで視覚的な引きを強化
- シナリオAIで生成されたキャッチコピーを使用
- **難易度**: 中 / **効果**: 高

#### Phase 3-B: 動画フレーム追加
- 動画を囲うように本の表紙やタイトルを表示
- ブランディング要素の追加
- 視覚的な統一感の向上
- **難易度**: 低〜中 / **効果**: 中

#### Phase 3-C: nanobana画像変換統合
- nanobanaを使ってimage to image変換
- プロモーション用の高品質画像を自動生成
- 画像クオリティの向上
- **難易度**: 高 / **効果**: 高

---

## 📋 終了したタスク

### Phase 5: Veo3音声対応動画 🎙️ ✅
**目標**: 人物が話す動画の生成
- Veo3を使って、入力した画像の人物が話す動画を生成
- リアルな音声リップシンク
- プロモーション動画の多様化

**実装完了内容:**
- 生成モジュール: [veo3_talking_video.py](src/generators/veo3_talking_video.py)
  - 入力画像 + 音声（またはTTS）でTalking Head動画を生成
  - プロンプトエンジニアリング用オプション（emotion/camera/style/language）
  - Veo 3.1の参照画像コンフィグを使用し、未対応環境では3.0形式にフォールバック
  - SDKが音声参照を未サポートな場合は、生成後に音声を自動でmux（後付け合成）
- UI: [main.py](src/ui/main.py) に2タブ構成で統合
  - Tab 1: Veo3 画像→動画 (Simple)
  - Tab 2: Veo3 Talking Video (口パク重視)
- テストスクリプト: `src/simpletest/test_veo3_talking.py`

**前提条件:**
- `GOOGLE_API_KEY` を設定
- TTSを使う場合は `GOOGLE_APPLICATION_CREDENTIALS` を設定

### Phase 4: シナリオ作成AI 🤖 ✅
**目標**: LLMを活用した自動ナレーション生成
- プロンプトエンジニアリングのデモンストレーション
- 8秒ショート動画用の質の高いナレーションテキスト生成

**実装完了内容:**
- 生成モジュール: [scenario_generator.py](src/generators/scenario_generator.py)
  - OpenAI GPT-4o/GPT-5 (gpt-5-chat-latest, gpt-4o) API統合
  - シンプルなプロンプト設計（システム+ユーザープロンプト統合）
  - 最小限のパラメータ（model + messages のみ）で高品質出力
  - 50〜60文字の最適なナレーション長
- UI: [scenario_app.py](src/ui/scenario_app.py) (ポート: 8501)
  - 書籍情報入力（タイトル、説明、ターゲット読者、雰囲気）
  - 宣伝スタイルカスタマイズ機能
  - モデル選択（gpt-5-chat-latest / gpt-4o）
  - 目標文字数調整機能
  - 生成結果の統計表示（文字数、最初の20文字、推定読み上げ時間）

**前提条件:**
- `.env`ファイルに `OPENAI_API_KEY` を設定

### Phase 1: Veo3検証 ✅
- image to videoの検証完了
- [veo3_sample.py](src/generators/veo3_sample.py): 画像入力で動画生成、プロンプト制御
- [main.py](src/ui/main.py): Streamlit UI実装

### Phase 2: スライドショー動画生成 ✅
- スライドショー形式のショート動画作成機能を実装
- 複数画像を順に表示、横スライド/パンアニメーション
- TTS統合による自動ナレーション生成
- BGM選択機能
- 字幕自動配置（ナレーション同期）
- 自然な日本語テキスト分割アルゴリズム
- [slideshow_app.py](src/ui/slideshow_app.py): Streamlit UI
- [slideshow_generator.py](src/generators/slideshow_generator.py): 動画生成ロジック
- [text_to_speech_client.py](src/generators/text_to_speech_client.py): Google Cloud TTS統合
