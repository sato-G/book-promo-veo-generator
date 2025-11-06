# システムアーキテクチャ設計書

## 概要

書籍プロモーション動画生成システムは、AI技術を活用して書籍の魅力を伝える動画を自動生成するシステムです。

## システム構成

```
┌─────────────────────────────────────────────┐
│         Streamlit UI Layer                  │
│  (ui/video_editor.py)                       │
└─────────────────┬───────────────────────────┘
                  │
    ┌─────────────┴──────────────┐
    │                            │
┌───▼──────────┐      ┌─────────▼──────────┐
│  Video Gen   │      │   Audio Gen        │
│  (Veo 3.1)   │      │   (TTS)            │
│              │      │                    │
│ veo_         │      │ tts_client.py      │
│ generator.py │      │                    │
└───┬──────────┘      └─────────┬──────────┘
    │                           │
    └────────┬──────────────────┘
             │
    ┌────────▼──────────┐
    │  Video Effects    │
    │  (MoviePy)        │
    │                   │
    │ moviepy_          │
    │ effects.py        │
    └───────────────────┘
```

## コンポーネント詳細

### 1. UI Layer（Streamlit）
- **責務**: ユーザーインターフェース、プレビュー、パラメータ調整
- **主要ファイル**: `ui/video_editor.py`
- **機能**:
  - 書籍情報入力（タイトル、表紙画像）
  - プロンプト編集
  - リアルタイムプレビュー
  - 動画エクスポート

### 2. Video Generation（Veo 3.1）
- **責務**: 静止画から動画への変換
- **主要ファイル**: `generators/veo_generator.py`
- **機能**:
  - Google Veo 3.1 API呼び出し
  - プロンプトベースの動画生成
  - ポーリングによる生成完了待機
  - 生成済み動画のダウンロード

### 3. Audio Generation（TTS）
- **責務**: ナレーション音声の生成
- **主要ファイル**: `generators/tts_client.py`
- **機能**:
  - Google Cloud Text-to-Speech API呼び出し
  - 日本語音声合成
  - 男性/女性の声選択
  - 音声ファイル出力

### 4. Video Effects（MoviePy）
- **責務**: 動画編集・エフェクト適用
- **主要ファイル**: `generators/moviepy_effects.py`
- **機能**:
  - テキストオーバーレイ
  - フェードイン/アウト
  - ズーム効果
  - 音声トラック合成

## データフロー

```
1. ユーザー入力
   ↓
2. 書籍表紙画像 + プロンプト → Veo 3.1 API
   ↓
3. 動画生成（ポーリング待機）
   ↓
4. ナレーションテキスト → TTS API
   ↓
5. MoviePyで合成（動画 + 音声 + テキスト）
   ↓
6. 最終動画出力
```

## 外部依存関係

### Google APIs
- **Veo 3.1 API**: 動画生成
  - 認証: Google API Key (`.env`で管理)
  - レート制限: 要確認
  - モデル: `veo-3.1-pro`

- **Cloud Text-to-Speech**: 音声合成
  - 認証: Application Default Credentials (ADC)
  - 言語: 日本語（ja-JP）
  - 音声: Wavenet/Neural2

### Pythonライブラリ
- `streamlit`: UIフレームワーク
- `moviepy`: 動画編集
- `google-generativeai`: Veo 3.1 API
- `google-cloud-texttospeech`: TTS API
- `Pillow`: 画像処理
- `python-dotenv`: 環境変数管理

## セキュリティ考慮事項

### 認証情報管理
- APIキーは`.env`で管理（`.gitignore`に追加）
- Google Cloud認証は`gcloud auth application-default login`で設定
- **絶対に禁止**: コードへのハードコーディング

### Fail-First原則
- API呼び出し失敗時は即座にエラー送出
- 異常な入力値は早期検証でreject
- try/exceptでのエラー握りつぶしは禁止

## パフォーマンス考慮事項

### ボトルネック
1. **Veo 3.1 API**: 動画生成に数分かかる（ポーリング必須）
2. **MoviePy**: 大きな動画の処理は時間がかかる
3. **TTS API**: ネットワーク遅延

### 最適化戦略
- 非同期処理の活用
- キャッシング（生成済み動画）
- プログレスバー表示でUX改善

## 拡張性

### 将来的な拡張
- 複数書籍の一括処理
- テンプレート機能（プロンプトプリセット）
- SNS直接投稿機能
- 多言語対応

## 技術的負債
現時点での技術的負債はなし。今後のコードレビューで随時確認。
