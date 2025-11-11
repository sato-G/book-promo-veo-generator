# Simple Test Scripts

各機能の簡易テストスクリプト置き場

## test_veo3.py

Veo 3.1動画生成の簡易テスト

### 使い方

```bash
# 基本的な実行
python simpletest/test_veo3.py --image path/to/image.png

# プロンプトを指定
python simpletest/test_veo3.py \
  --image path/to/image.png \
  --prompt "カメラが本に近づいていく"

# 長さを指定（4, 6, 8秒）
python simpletest/test_veo3.py \
  --image path/to/image.png \
  --duration 6
```

### 必要な準備

```bash
# API Keyを設定
export GOOGLE_API_KEY=your_api_key

# 仮想環境をアクティベート
source venv/bin/activate
```

## 今後のテストスクリプト

- `test_text_to_speech.py` - 音声生成のテスト
- `test_video_processing.py` - 動画編集のテスト
- など...

## 追加: Veo 画像 + プロンプト テスト (Simple)

`test_veo3_talking.py` は、画像とプロンプトのみで動画を生成する最小テストです。

使い方:

```bash
cd src/simpletest

# 画像 + プロンプト
python test_veo3_talking.py \
  --image ../data/image_sample/test1.jpg \
  --prompt "被写体の一貫性を保ち、自然なカメラワークで魅力を伝える"
```

準備:

```bash
export GOOGLE_API_KEY=your_api_key
```

実装: `src/generators/veo3_talking_video.py`（シンプル版）
