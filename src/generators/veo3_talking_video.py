#!/usr/bin/env python3
"""
Veo 3.x 画像 + プロンプト → 動画（シンプル版）

最小要件: 入力画像とプロンプトだけで動画を生成。
プロンプトはCLI引数、または下部の定数 PROMPT を編集して使えます。
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
    from google.genai import types
except Exception as e:
    raise SystemExit(
        f"google-genai import error: {e}\nInstall with: pip install google-genai google-generativeai"
    )


# ここを編集して固定プロンプトとして使うこともできます
PROMPT: str = "被写体の一貫性を保ちつつ、滑らかで自然なカメラワークで本の魅力を伝える短い動画を生成する。"


def _check_api_key() -> None:
    if not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit(
            "ERROR: GOOGLE_API_KEY not set.\nSet with: export GOOGLE_API_KEY=your_api_key"
        )


def _timestamped_outpath(prefix: str, suffix: str, outdir: Path) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return outdir / f"{prefix}_{ts}{suffix}"


def generate_video(
    image_path: Path,
    prompt: str,
    *,
    output_dir: Path = Path("data/output"),
    model: str = "veo-3.0-generate-001",
) -> Path:
    """
    画像 + プロンプトから動画を生成（シンプル）

    Args:
        image_path: 入力画像のパス
        prompt: Veoへのプロンプト（自由に編集）
        output_dir: 出力ディレクトリ
        model: 使用モデル（既定: veo-3.0-generate-001）
    Returns:
        出力動画のPath
    """
    _check_api_key()

    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    print("\n" + "=" * 60)
    print("🎥 Veo 画像→動画 生成 (Simple)")
    print("=" * 60)
    print(f"画像: {image_path}")
    print(f"モデル: {model}")
    print(f"プロンプト: {prompt}")
    print("=" * 60 + "\n")

    client = genai.Client()

    mime = "image/png" if image_path.suffix.lower() == ".png" else "image/jpeg"
    image_bytes = image_path.read_bytes()
    image = types.Image(imageBytes=image_bytes, mimeType=mime)

    # もっともシンプルな呼び出し（3.0形式）
    operation = client.models.generate_videos(
        model=model,
        prompt=prompt,
        image=image,
    )

    # 完了待ち
    waited = 0
    while not getattr(operation, "done", False):
        waited += 10
        print(f"⏳ 生成中... ({waited}s)")
        time.sleep(10)
        operation = client.operations.get(operation)

    result = getattr(operation, "result", None) or getattr(operation, "response", None)
    if not result or not getattr(result, "generated_videos", None):
        raise RuntimeError("Video generation failed: no result")

    gen_video = result.generated_videos[0]
    client.files.download(file=gen_video.video)

    out_path = _timestamped_outpath("veo3_simple", ".mp4", output_dir)
    gen_video.video.save(str(out_path))

    print("\n" + "=" * 60)
    print("✅ 生成完了")
    print("=" * 60)
    print(f"出力: {out_path}")
    print("=" * 60 + "\n")
    return out_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Veo 画像+プロンプト → 動画 (Simple)")
    parser.add_argument("--image", type=Path, required=True, help="入力画像のパス")
    parser.add_argument("--prompt", type=str, help="Veoへのプロンプト（未指定なら定数PROMPTを使用）")
    parser.add_argument("--model", type=str, default="veo-3.0-generate-001")
    parser.add_argument("--output", type=Path, default=Path("data/output"))

    args = parser.parse_args()

    p = args.prompt if args.prompt else PROMPT
    try:
        out = generate_video(
            image_path=args.image,
            prompt=p,
            output_dir=args.output,
            model=args.model,
        )
        print(f"✅ 出力: {out}")
    except Exception as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
