# 書籍プロモーション動画生成システム - 仕様書

**バージョン**: 3.0
**最終更新**: 2025-11-12
**ステータス**: Active

---

## 📋 現在のタスク

### Phase 4: シナリオ作成AI 🤖 ⭐️ 最優先

**目標**: LLMを活用した自動シナリオ生成
- プロンプトエンジニアリングのデモンストレーション
- シナリオ生成がアニメーション設計の基盤となる

**実装内容:**
- 書籍情報を入力として受け取る（タイトル、説明、ターゲット、雰囲気）
- OpenAI GPT-4o/GPT-5 APIを使用してシナリオ自動生成（冒頭インパクト用キャッチコピーが最初に出力）

- **技術**: OpenAI API (GPT-4o/GPT-5)
- **難易度**: 中 / **効果**: 非常に高

**次のステップ:**
- `feature/scenario-generator` ブランチで開発
- プロンプトエンジニアリングで高品質な出力を実現


---

## 📋 次期タスク（Phase 3, 5以降）

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

### Phase 5: Veo3音声対応動画 🎙️
**目標**: 人物が話す動画の生成
- Veo3を使って、入力した画像の人物が話す動画を生成
- リアルな音声リップシンク
- プロモーション動画の多様化
- **難易度**: 高 / **効果**: 高

- 残りタスク
    - Veo3プロンプト案を提案（オプション）
    - 各画像のヒント・イメージ提案を出力

実装済み（初期版）:
- 生成モジュール: `src/generators/veo3_talking_video.py`
  - 入力画像 + 音声（またはTTS）でTalking Head動画を生成
  - プロンプトエンジニアリング用オプション（emotion/camera/style/language）
  - Veo 3.1の参照画像コンフィグを使用し、未対応環境では3.0形式にフォールバック
  - SDKが音声参照を未サポートな場合は、生成後に音声を自動でmux（後付け合成）

簡易テスト:
- `src/simpletest/test_veo3_talking.py`
- 例: `python src/simpletest/test_veo3_talking.py --image data/image_sample/test1.jpg --text "本の魅力を紹介します"`

前提:
- `GOOGLE_API_KEY` を設定
- TTSを使う場合は `GOOGLE_APPLICATION_CREDENTIALS` を設定

---

## 📋 終了したタスク

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
