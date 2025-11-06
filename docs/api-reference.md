# API仕様書

## 概要

本ドキュメントは、書籍プロモーション動画生成システムの内部APIを定義します。

## generators/veo_generator.py

### `generate_video_from_image`

```python
def generate_video_from_image(
    image_path: str,
    prompt: str,
    output_path: str,
    duration: int = 5
) -> str:
    """
    静止画からVeo 3.1を使って動画を生成

    Args:
        image_path: 入力画像のパス（PNG, JPG対応）
        prompt: 動画生成プロンプト（例: "Soldier marching forward"）
        output_path: 出力動画パス（.mp4）
        duration: 動画長さ（秒）デフォルト5秒

    Returns:
        生成された動画ファイルのパス

    Raises:
        FileNotFoundError: 画像ファイルが存在しない（Fail-First）
        ValueError: durationが1〜10秒の範囲外（Fail-First）
        APIError: Veo API呼び出し失敗
        TimeoutError: 生成がタイムアウト（5分超過）

    Example:
        >>> video_path = generate_video_from_image(
        ...     "book_cover.png",
        ...     "Zoom into the book cover slowly",
        ...     "output/promo.mp4",
        ...     duration=5
        ... )
        >>> print(video_path)
        "output/promo.mp4"
    """
```

### `wait_for_generation`

```python
def wait_for_generation(
    operation_id: str,
    timeout: int = 300
) -> dict:
    """
    Veo動画生成の完了を待機（ポーリング）

    Args:
        operation_id: Veo API返却のオペレーションID
        timeout: タイムアウト時間（秒）デフォルト300秒

    Returns:
        生成結果の辞書
        {
            "status": "SUCCESS",
            "video_url": "https://...",
            "duration": 5.2
        }

    Raises:
        TimeoutError: 指定時間内に完了しない（Fail-First）
        APIError: 生成が失敗

    Example:
        >>> result = wait_for_generation("op-12345", timeout=300)
        >>> print(result["status"])
        "SUCCESS"
    """
```

## generators/tts_client.py

### `generate_speech`

```python
def generate_speech(
    text: str,
    output_path: str,
    language_code: str = "ja-JP",
    voice_name: str = "ja-JP-Wavenet-C",
    speaking_rate: float = 1.0
) -> str:
    """
    テキストから音声を生成（Google Cloud TTS）

    Args:
        text: 読み上げテキスト（最大5000文字）
        output_path: 出力音声ファイルパス（.mp3）
        language_code: 言語コード（デフォルト: 日本語）
        voice_name: 音声名
            - "ja-JP-Wavenet-C": 男性（低音）
            - "ja-JP-Wavenet-B": 女性（標準）
        speaking_rate: 話速（0.25〜4.0）デフォルト1.0

    Returns:
        生成された音声ファイルのパス

    Raises:
        ValueError: textが空または5000文字超過（Fail-First）
        ValueError: speaking_rateが範囲外（Fail-First）
        AuthenticationError: Google Cloud認証失敗
        APIError: TTS API呼び出し失敗

    Example:
        >>> audio_path = generate_speech(
        ...     "この本は、あなたの人生を変える一冊です。",
        ...     "output/narration.mp3",
        ...     voice_name="ja-JP-Wavenet-C"
        ... )
        >>> print(audio_path)
        "output/narration.mp3"
    """
```

### 利用可能な音声一覧

| voice_name | 性別 | 特徴 | 用途 |
|------------|------|------|------|
| `ja-JP-Wavenet-A` | 女性 | 明るい | 軽快な本 |
| `ja-JP-Wavenet-B` | 女性 | 標準 | 汎用 |
| `ja-JP-Wavenet-C` | 男性 | 低音 | 重厚な本 |
| `ja-JP-Wavenet-D` | 男性 | 標準 | ビジネス書 |
| `ja-JP-Neural2-B` | 女性 | 自然 | 科学書 |
| `ja-JP-Neural2-C` | 男性 | 自然 | ドキュメンタリー |

## generators/moviepy_effects.py

### `add_text_overlay`

```python
def add_text_overlay(
    video_clip: VideoClip,
    text: str,
    position: tuple[int, int] | str = "center",
    fontsize: int = 70,
    color: str = "white",
    duration: float | None = None,
    start_time: float = 0.0
) -> VideoClip:
    """
    動画にテキストオーバーレイを追加

    Args:
        video_clip: 対象の動画クリップ
        text: 表示テキスト
        position: 位置（"center", "bottom"など）またはピクセル座標
        fontsize: フォントサイズ（デフォルト70）
        color: 文字色（"white", "black"など）
        duration: 表示時間（None = 動画全体）
        start_time: 開始時刻（秒）

    Returns:
        テキストが追加された動画クリップ

    Raises:
        ValueError: fontsizeが0以下（Fail-First）
        ValueError: start_timeが負（Fail-First）

    Example:
        >>> video = VideoFileClip("input.mp4")
        >>> video_with_text = add_text_overlay(
        ...     video,
        ...     "続きは本書で",
        ...     position="bottom",
        ...     fontsize=80
        ... )
    """
```

### `add_fade_effect`

```python
def add_fade_effect(
    video_clip: VideoClip,
    fade_in_duration: float = 1.0,
    fade_out_duration: float = 1.0
) -> VideoClip:
    """
    フェードイン/アウト効果を追加

    Args:
        video_clip: 対象の動画クリップ
        fade_in_duration: フェードイン時間（秒）
        fade_out_duration: フェードアウト時間（秒）

    Returns:
        フェード効果が追加された動画クリップ

    Raises:
        ValueError: durationが負（Fail-First）
        ValueError: durationが動画長より長い（Fail-First）

    Example:
        >>> video = VideoFileClip("input.mp4")
        >>> video_with_fade = add_fade_effect(video, 1.5, 1.5)
    """
```

### `compose_video_with_audio`

```python
def compose_video_with_audio(
    video_path: str,
    audio_path: str,
    output_path: str,
    video_volume: float = 0.5,
    audio_volume: float = 1.0
) -> str:
    """
    動画と音声を合成

    Args:
        video_path: 入力動画パス
        audio_path: 入力音声パス（.mp3, .wav対応）
        output_path: 出力動画パス（.mp4）
        video_volume: 動画音声ボリューム（0.0〜1.0）
        audio_volume: ナレーション音声ボリューム（0.0〜1.0）

    Returns:
        合成された動画ファイルのパス

    Raises:
        FileNotFoundError: 入力ファイルが存在しない（Fail-First）
        ValueError: volumeが0.0〜1.0の範囲外（Fail-First）

    Example:
        >>> output = compose_video_with_audio(
        ...     "promo_video.mp4",
        ...     "narration.mp3",
        ...     "final_output.mp4",
        ...     video_volume=0.3,
        ...     audio_volume=1.0
        ... )
    """
```

## ui/video_editor.py

### Streamlit UI API

Streamlit UIは直接呼び出すAPIではありませんが、主要なコンポーネントを記載します。

#### UI Components

1. **書籍情報入力**
   - タイトル入力
   - 表紙画像アップロード
   - ナレーションテキスト入力

2. **動画生成パラメータ**
   - Veoプロンプト入力
   - 動画長さ選択（1〜10秒）
   - 音声選択（男性/女性）

3. **プレビュー**
   - 生成済み動画プレビュー
   - 音声再生

4. **エクスポート**
   - 最終動画生成
   - ダウンロードボタン

## エラーハンドリング

### エラークラス階層

```python
class VideoGeneratorError(Exception):
    """基底例外クラス"""
    pass

class APIError(VideoGeneratorError):
    """API呼び出し失敗"""
    pass

class AuthenticationError(APIError):
    """認証失敗"""
    pass

class TimeoutError(VideoGeneratorError):
    """タイムアウト"""
    pass

class ValidationError(VideoGeneratorError):
    """入力値検証エラー（Fail-First）"""
    pass
```

### エラー処理の原則（Fail-First）

```python
# ❌ 悪い例（エラー握りつぶし）
try:
    result = generate_video(image_path, prompt)
except Exception:
    return None  # 失敗を隠蔽

# ✅ 良い例（早期失敗）
def generate_video(image_path: str, prompt: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    if not prompt.strip():
        raise ValueError("Prompt must not be empty")

    # 処理続行（エラーは上位に伝播）
    return veo_api.generate(image_path, prompt)
```

## レート制限

### Veo 3.1 API
- リクエスト数: 未確認（要調査）
- 同時実行: 1リクエストずつ推奨

### TTS API
- リクエスト数: 300回/分
- 文字数: 1リクエストあたり5000文字まで

## バージョニング

内部APIはセマンティックバージョニングに従います：
- **MAJOR**: 破壊的変更
- **MINOR**: 後方互換性のある機能追加
- **PATCH**: バグ修正

現在のバージョン: `v1.0.0`
