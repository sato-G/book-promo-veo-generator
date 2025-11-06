#!/usr/bin/env python3
"""
Veo 3.1 動画生成サンプル

書籍表紙画像から動画を生成するシンプルなサンプルコード。

使い方:
    export GOOGLE_API_KEY=your_api_key
    python veo3_sample.py --image path/to/book_cover.png --prompt "動画生成のプロンプト"
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Fail-First: 依存ライブラリのインポートエラーを早期検出
try:
    from google import genai
    from google.genai import types
except ImportError as e:
    raise SystemExit(
        f"Required library not found: {e}\n"
        "Install with: pip install google-generativeai"
    )


def generate_video(
    image_path: Path,
    prompt: str,
    output_dir: Path = Path("output"),
    duration: int = 8
) -> Path:
    """
    Veo 3.1で動画生成

    Args:
        image_path: 入力画像パス（PNG/JPG）
        prompt: 動画生成プロンプト
        output_dir: 出力ディレクトリ
        duration: 動画長さ（秒）デフォルト8秒

    Returns:
        生成された動画ファイルのパス

    Raises:
        SystemExit: 環境変数GOOGLE_API_KEYが未設定
        FileNotFoundError: 画像ファイルが存在しない
        ValueError: durationが無効な値
    """
    # Fail-First: 入力検証
    if not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit(
            "ERROR: GOOGLE_API_KEY not set in environment.\n"
            "Set with: export GOOGLE_API_KEY=your_api_key"
        )

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    if not 4 <= duration <= 8:
        raise ValueError(f"Duration must be 4-8 seconds, got {duration}")

    print(f"\n{'='*60}")
    print(f"🎥 Veo 3.1 動画生成")
    print(f"{'='*60}")
    print(f"入力画像: {image_path}")
    print(f"プロンプト: {prompt}")
    print(f"動画長さ: {duration}秒")
    print(f"{'='*60}\n")

    # Google Generative AI Client初期化
    client = genai.Client()

    # 画像をバイナリで読み込み
    mime_type = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
    image_bytes = image_path.read_bytes()
    image = types.Image(imageBytes=image_bytes, mimeType=mime_type)

    # リファレンス画像として設定
    reference = types.VideoGenerationReferenceImage(
        image=image,
        referenceType=types.VideoGenerationReferenceType.ASSET,
    )

    # 動画生成設定
    config = types.GenerateVideosConfig(
        referenceImages=[reference],
        durationSeconds=duration,
    )

    # 動画生成開始
    print("⏳ 動画生成を開始...")
    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt,
        config=config,
    )

    # ポーリングで完了を待機
    wait_count = 0
    while not operation.done:
        wait_count += 1
        print(f"⏳ 生成中... ({wait_count * 10}秒経過)")
        time.sleep(10)
        operation = client.operations.get(operation)

    # 結果確認（Fail-First）
    if not getattr(operation, 'response', None):
        raise SystemExit(
            "ERROR: Video generation failed. No response returned.\n"
            "Try a simpler prompt or check API quota."
        )

    if not getattr(operation.response, 'generated_videos', None):
        raise SystemExit(
            "ERROR: Video generation failed. No video returned.\n"
            "Try relaxing constraints in the prompt."
        )

    # 生成された動画を取得
    video = operation.response.generated_videos[0]
    client.files.download(file=video.video)

    # 出力ファイル名生成
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_path = output_dir / f"veo3_{timestamp}.mp4"

    # 動画保存
    video.video.save(str(output_path))

    print(f"\n{'='*60}")
    print(f"✅ 動画生成完了")
    print(f"{'='*60}")
    print(f"出力: {output_path}")
    print(f"サイズ: {output_path.stat().st_size / (1024*1024):.2f} MB")
    print(f"{'='*60}\n")

    return output_path


def main():
    """コマンドライン引数を処理してVeo 3.1で動画生成"""
    parser = argparse.ArgumentParser(
        description="Veo 3.1で書籍表紙画像から動画を生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 基本的な使い方
  python veo3_sample.py --image book_cover.png --prompt "本のタイトルが浮かび上がる"

  # 動画長さを指定
  python veo3_sample.py --image book_cover.png --prompt "ズームイン" --duration 6

  # 出力ディレクトリを指定
  python veo3_sample.py --image book_cover.png --prompt "回転" --output custom_output/
        """
    )

    parser.add_argument(
        "--image",
        type=Path,
        required=True,
        help="入力画像パス（書籍表紙など）"
    )

    parser.add_argument(
        "--prompt",
        type=str,
        required=True,
        help="動画生成プロンプト（例: 'カメラが本に近づく'）"
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output"),
        help="出力ディレクトリ（デフォルト: output/）"
    )

    parser.add_argument(
        "--duration",
        type=int,
        default=8,
        choices=[4, 6, 8],
        help="動画長さ（秒）デフォルト: 8"
    )

    args = parser.parse_args()

    # 動画生成実行
    try:
        output_path = generate_video(
            image_path=args.image,
            prompt=args.prompt,
            output_dir=args.output,
            duration=args.duration
        )
        print(f"✅ 成功: {output_path}")
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
