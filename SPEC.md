# 書籍プロモーション動画生成システム - 仕様書

**バージョン**: 4.0
**最終更新**: 2025-11-12
**ステータス**: Active

---

## 📋 現在のタスク
最後のチェック（やりたいことができているか）
- ユースケース
  - 『あの戦争は何だったのか』
    - 実際の写真を用いたショート動画生成
    - インパクトのある宣伝内容
  - 『土と生命の46億年史』 
    - 作者が話すとかできるのか
  - 『「腸と脳」の科学』
    - 解説→本のタイトルという流れができるか。
- streamlitに必要なプログラム
 - 内容を入力して、8秒の宣伝動画のシナリオを出力するプログラム
 - 最初の2秒で、視聴者を惹きつけるアニメーションができるプログラム
 - 実際の写真を用いて本の解説をするプログラム
 - 写真の人物が話すプログラム
 - 解説ができるプログラム
 - 画像生成ができるプログラム
 - 作成した動画をオーバーレイするプログラム
 - 本の宣伝として最後の3秒を使うプログラム
 - 動画どうしを繋げるプログラム


## 📋 終了したタスク

### Phase 3: アニメーション強化とUI改善 🎬 ✅
**目標**: スライドショー動画のクオリティ向上と視覚的インパクトの強化

**実装完了内容:**
- **冒頭アニメーション**: [opening_animation_generator.py](src/generators/opening_animation_generator.py)
  - 360度回転しながらズームバックする迫力のある演出
  - キャッチコピー字幕の焼き込み（黄色ゴールド、フォントサイズ100pt）
  - TTSナレーション統合（オプション）
  - 2秒構成: 0.2秒アニメーション + 1.8秒静止
  - テストスクリプト: `src/simpletest/test_opening_animation.py`

- **動画オーバーレイ**: [video_overlay_generator.py](src/generators/video_overlay_generator.py)
  - 動画に白い余白を追加（レターボックス効果）
  - 表紙画像のオーバーレイ配置（静止/浮遊アニメーション）
  - 上部白帯 + 字幕表示機能（オプション、今後の展開用）
  - テストスクリプト: `src/simpletest/test_video_overlay.py`

- **動画フレーム**: [video_frame_generator.py](src/generators/video_frame_generator.py)
  - 動画周囲にブランディング要素を追加
  - タイトル、表紙、著者名の統合表示
  - テストスクリプト: `src/simpletest/test_video_frame.py`

- **字幕位置最適化**: [slideshow_generator.py](src/generators/slideshow_generator.py)
  - 字幕位置を中央配置に変更（オーバーレイとの互換性向上）
  - 動画単体でもオーバーレイ適用後も見やすい位置に自動調整

- **動画連結機能**: [video_concat.py](src/generators/video_concat.py)
  - 複数動画を順番に連結するユーティリティ
  - UI: [main.py](src/ui/main.py) Concat Videosタブ

- **Text to Image統合**: [main.py](src/ui/main.py)
  - Gemini Text to ImageタブでAI画像生成
  - nanobanaクライアント統合済み

**Streamlit UI統合状況:**
全機能を単一のUI（`src/ui/main.py`）に統合済み。利用順でタブを配置し、主要パラメータはUIから設定できます。

- Scenario（シナリオ生成）: OpenAIで短尺ナレーション生成
- Text to Image: nanobana CLI / Gemini API（GOOGLE_API_KEY）
- Quick Slideshow: 複数画像から短尺スライドショー（字幕/TTSなし）
- Explainer Slideshow: 長文→自動分割→字幕/TTS→スライド、書影＋最終タイトル対応
- Opening Animation: 画像→回転ズームバック（字幕/TTS可）
- Overlay: 動画に表紙等を重ねる（位置/スケール/アニメ/帯/字幕）
- Frame: 動画にフレーム＋タイトル＋表紙（ブランド化）
- Cover Card: 表紙＋タイトルの締めカット（字幕位置/色/サイズ、TTS）
- Veo3 画像→動画 (Simple): 画像＋プロンプトのシンプル生成
- Veo3 Talking Video: 画像＋プロンプト（ふりがなテンプレ例）
- Concat Videos: 複数動画を順に連結（FPS/解像度統一可）

実行: `streamlit run src/ui/main.py`

**前提条件:**
- Google Cloud TTS: `GOOGLE_APPLICATION_CREDENTIALS` を設定

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
