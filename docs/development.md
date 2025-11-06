# 開発ガイド

## セットアップ

### 前提条件
- Python 3.9以上
- Google Cloud アカウント
- Google API Key（Veo 3.1用）

### 環境構築

```bash
# リポジトリクローン
git clone <repository-url>
cd book-promo-veo-generator

# 仮想環境作成
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .envファイルにAPIキーを記載
```

### Google Cloud認証

```bash
# Application Default Credentials設定
gcloud auth application-default login

# プロジェクト設定
gcloud config set project YOUR_PROJECT_ID
```

## 開発フロー

### 1. 新機能開発

```bash
# developブランチから開始
git checkout develop
git pull origin develop

# featureブランチ作成
git checkout -b feature/123-new-feature

# 開発開始
```

### 2. ドキュメント駆動開発

**重要**: コードを書く前にドキュメントを書く

#### ステップ1: 仕様書作成
新機能の場合、`docs/api-reference.md`に追記：

```markdown
## 新機能：字幕アニメーション

### 概要
字幕にフェードイン効果を追加する機能

### API
\`\`\`python
def add_subtitle_animation(
    video_clip: VideoClip,
    text: str,
    duration: float = 2.0,
    fade_duration: float = 0.5
) -> VideoClip:
    """
    字幕をフェードイン効果付きで追加

    Args:
        video_clip: 対象動画クリップ
        text: 字幕テキスト
        duration: 字幕表示時間（秒）
        fade_duration: フェードイン時間（秒）

    Returns:
        字幕追加後の動画クリップ

    Raises:
        ValueError: durationが0以下の場合（Fail-First）
    """
\`\`\`
```

#### ステップ2: テストケース設計
コードを書く前にテストを設計：

```python
# tests/test_subtitle_animation.py
import pytest

def test_add_subtitle_animation_normal():
    """正常系: 字幕が追加される"""
    pass  # TODO: 実装

def test_add_subtitle_animation_invalid_duration():
    """異常系: duration=0でValueError（Fail-First）"""
    with pytest.raises(ValueError):
        add_subtitle_animation(video_clip, "test", duration=0)
```

#### ステップ3: 実装
ドキュメントとテストに従って実装：

```python
# generators/moviepy_effects.py

def add_subtitle_animation(
    video_clip: VideoClip,
    text: str,
    duration: float = 2.0,
    fade_duration: float = 0.5
) -> VideoClip:
    # Fail-First: 早期エラー検出
    if duration <= 0:
        raise ValueError(f"duration must be positive, got {duration}")

    if fade_duration < 0 or fade_duration > duration:
        raise ValueError(
            f"fade_duration must be 0 <= fade_duration <= duration, "
            f"got fade_duration={fade_duration}, duration={duration}"
        )

    # 実装
    txt_clip = TextClip(text, fontsize=70, color='white')
    txt_clip = txt_clip.set_position('center').set_duration(duration)
    txt_clip = txt_clip.fadein(fade_duration)

    return CompositeVideoClip([video_clip, txt_clip])
```

### 3. Fail-First原則の実践

#### ❌ 悪い例（エラー握りつぶし）
```python
def generate_video(image_path: str):
    try:
        # Veo API呼び出し
        response = veo_api.generate(image_path)
        return response
    except Exception as e:
        # エラーを握りつぶす（禁止！）
        print(f"Error: {e}")
        return None  # 失敗を隠蔽
```

#### ✅ 良い例（早期失敗）
```python
def generate_video(image_path: str) -> str:
    """
    動画生成

    Raises:
        FileNotFoundError: 画像ファイルが存在しない
        APIError: Veo API呼び出し失敗
    """
    # 入力検証（Fail-First）
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    # API呼び出し（エラーは上位で処理）
    response = veo_api.generate(image_path)

    if response.status != "SUCCESS":
        raise APIError(f"Veo API failed: {response.error_message}")

    return response.video_url
```

### 4. コーディング規約

#### Pythonスタイル
- PEP 8準拠
- 型ヒント必須
- Docstring（Google形式）必須

```python
def process_video(
    input_path: str,
    output_path: str,
    effects: list[str]
) -> bool:
    """
    動画処理

    Args:
        input_path: 入力動画パス
        output_path: 出力動画パス
        effects: 適用エフェクト一覧

    Returns:
        成功時True、失敗時False

    Raises:
        ValueError: effectsが空の場合（Fail-First）
    """
    if not effects:
        raise ValueError("effects must not be empty")

    # 実装
```

#### ファイル構成
```
generators/
├── __init__.py
├── veo_generator.py       # Veo 3.1 API
├── tts_client.py          # TTS API
└── moviepy_effects.py     # 動画エフェクト

ui/
└── video_editor.py        # Streamlit UI

tests/
├── test_veo_generator.py
├── test_tts_client.py
└── test_moviepy_effects.py
```

### 5. テスト

```bash
# テスト実行
pytest tests/

# カバレッジ確認
pytest --cov=generators tests/
```

### 6. デバッグ

#### Streamlit UIでのデバッグ
```bash
# 開発モードで起動
streamlit run ui/video_editor.py --logger.level=debug
```

#### ログ出力
```python
import logging

logger = logging.getLogger(__name__)

def generate_video(image_path: str):
    logger.info(f"Generating video from {image_path}")

    try:
        result = veo_api.generate(image_path)
        logger.info("Video generation successful")
        return result
    except APIError as e:
        logger.error(f"API error: {e}", exc_info=True)
        raise  # Fail-First: 再送出
```

## コードレビュー基準

### レビュー観点
1. **Fail-First原則**: エラーハンドリングは適切か？
2. **YAGNI**: 不要な機能を実装していないか？
3. **DRY**: 重複コードはないか？
4. **型ヒント**: すべての関数に型が付いているか？
5. **ドキュメント**: Docstringは明確か？
6. **テスト**: 重要な機能にテストがあるか？

### レビューチェックリスト
- [ ] Fail-First原則に従っている
- [ ] try/exceptでエラーを握りつぶしていない
- [ ] 型ヒントが適切
- [ ] Docstringが明確
- [ ] テストが追加されている
- [ ] CLAUDE.mdの原則に従っている
- [ ] 不要なコードが削除されている

## トラブルシューティング

### Veo API タイムアウト
```python
# リトライロジック（ただしFail-Fastを保つ）
import time

MAX_RETRIES = 3
RETRY_DELAY = 5

for attempt in range(MAX_RETRIES):
    try:
        result = veo_api.generate(image_path)
        break
    except TimeoutError as e:
        if attempt == MAX_RETRIES - 1:
            raise  # 最後は必ず失敗させる（Fail-First）
        logger.warning(f"Timeout, retrying... ({attempt+1}/{MAX_RETRIES})")
        time.sleep(RETRY_DELAY)
```

### TTS認証エラー
```bash
# ADC再設定
gcloud auth application-default login

# 環境変数確認
echo $GOOGLE_APPLICATION_CREDENTIALS
```

## リソース

- [Google Veo 3.1 API Documentation](https://ai.google.dev/veo)
- [Google Cloud TTS Documentation](https://cloud.google.com/text-to-speech/docs)
- [MoviePy Documentation](https://zulko.github.io/moviepy/)
- [Streamlit Documentation](https://docs.streamlit.io/)
