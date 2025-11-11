#!/usr/bin/env python3
"""
Veo 3.x 画像 + プロンプト → 動画（シンプル）テスト

使い方:
    cd src/simpletest
    python test_veo3_talking.py --image ../data/image_sample/test1.jpg \
      --prompt "被写体の一貫性を保ち、自然なカメラワークで魅力を伝える"
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.generators.veo3_talking_video import generate_video


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Veo 画像+プロンプト → 動画 (Simple) テスト")
    parser.add_argument("--image", type=Path, required=True, help="入力画像パス")
    parser.add_argument("--prompt", type=str, required=True, help="Veoへのプロンプト")
    parser.add_argument("--model", type=str, default="veo-3.0-generate-001")
    parser.add_argument("--output", type=Path, default=project_root/"data/output")

    args = parser.parse_args()

    out = generate_video(
        image_path=args.image,
        prompt=args.prompt,
        output_dir=args.output,
        model=args.model,
    )

    print(f"✅ 出力: {out}")


if __name__ == "__main__":
    main()
