#!/usr/bin/env python3
"""
Gemini Text-to-Image (CLI)

Gemini 2.5 Flash Image を使ってテキストから画像を生成します。

使い方:
  export GOOGLE_API_KEY=...
  python -m src.generators.gemini_text_to_image \
    --prompt "Create a picture of a nano banana dish in a fancy restaurant with a Gemini theme" \
    --n 2 \
    --output-dir data/generated/gemini
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()

try:
    from google import genai
except Exception as e:
    raise SystemExit(
        f"google-genai import error: {e}\nInstall with: pip install google-genai google-generativeai"
    )


def check_api_key() -> None:
    if not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit(
            "ERROR: GOOGLE_API_KEY not set. Set with: export GOOGLE_API_KEY=your_api_key"
        )


def save_parts_as_images(parts, outdir: Path, basename: str) -> List[Path]:
    """レスポンスの parts から画像を抽出して保存"""
    outdir.mkdir(parents=True, exist_ok=True)
    saved: List[Path] = []
    idx = 1
    for part in parts:
        try:
            if getattr(part, "inline_data", None) is not None:
                img = part.as_image()
                out = outdir / f"{basename}_{idx:02d}.png"
                img.save(str(out))
                saved.append(out)
                idx += 1
            elif getattr(part, "text", None):
                # 補足テキストがあれば出力
                print(part.text)
        except Exception as e:
            print(f"⚠️  skip part: {e}")
    return saved


def generate_images(
    *,
    prompt: str,
    n: int = 1,
    model: str = "gemini-2.5-flash-image",
    output_dir: Path = Path("data/generated/gemini"),
) -> List[Path]:
    check_api_key()
    client = genai.Client()

    all_saved: List[Path] = []
    for i in range(n):
        print(f"⏳ Generating image {i+1}/{n} ...")
        resp = client.models.generate_content(
            model=model,
            contents=[prompt],
        )
        ts = int(time.time())
        basename = f"gemini_{ts}_{i+1:02d}"
        saved = save_parts_as_images(resp.parts, output_dir, basename)
        if not saved:
            print("⚠️  No image part returned; check model access/usage policy")
        all_saved.extend(saved)

    return all_saved


def main():
    import argparse

    p = argparse.ArgumentParser(description="Gemini Text-to-Image (CLI)")
    p.add_argument("--prompt", type=str, required=True, help="画像生成プロンプト")
    p.add_argument("--n", type=int, default=1, help="生成枚数（連続呼び出し）")
    p.add_argument("--model", type=str, default="gemini-2.5-flash-image")
    p.add_argument("--output-dir", type=Path, default=Path("data/generated/gemini"))
    args = p.parse_args()

    try:
        paths = generate_images(
            prompt=args.prompt,
            n=args.n,
            model=args.model,
            output_dir=args.output_dir,
        )
        if paths:
            print("\n✅ Saved:")
            for pth in paths:
                print(str(pth))
        else:
            print("❌ No images saved")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

