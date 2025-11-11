#!/usr/bin/env python3
"""
Veo 3.x 画像 + プロンプト → 動画（シンプル版）

最小要件: 入力画像とプロンプトだけで動画を生成。
プロンプトはCLI引数、または定数 DEFAULT_PROMPT を編集して使えます。
画像パスは CLI 省略時に DEFAULT_IMAGE（絶対パス）を使用します。
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


# ここを編集して固定値として使えます（CLI未指定時に適用）
DEFAULT_IMAGE: Path = Path("/Users/sato/work/book-promo-veo-generator/data/『土と生命の46億年史』 /images/藤井一至さんエリマキ写真 (1).JPG")
DEFAULT_PROMPT: str = (
    "ショット: 正面の頭部〜肩のクローズアップ。カメラは固定し、揺れや過度なズームは避ける。\n"
    "被写体: 入力画像の人物。顔の造形・髪型・衣服の一貫性を保つ。自然なまばたきと微細な表情。\n"
    "口の動き: セリフと正確に同期。日本語の母音・子音の口形を丁寧に再現し、過度な頭の揺れは避ける。\n"
    "会話: 「記憶力の低下、不眠、うつ、発達障害、肥満、高血圧、糖尿病、感染症の重症化……\n"
    "すべての不調は腸から始まる!」\n"
    "SFX: 服がわずかに擦れる小さな音、口の開閉に伴うごく小さなブレス。\n"
    "周囲の音: 静かな室内の空気感。不要な雑音は入れない。\n"
    "長さ: およそ6秒。\n"
    "スタイル: 実写的で自然。圧縮歪みや口元の破綻、フレームのちらつきを避ける。"
)


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
    parser.add_argument("--image", type=Path, required=False, help="入力画像のパス（未指定時はDEFAULT_IMAGE）")
    parser.add_argument("--prompt", type=str, help="Veoへのプロンプト（未指定ならDEFAULT_PROMPT）")
    parser.add_argument("--model", type=str, default="veo-3.0-generate-001")
    parser.add_argument("--output", type=Path, default=Path("data/output"))

    args = parser.parse_args()

    img = args.image if args.image else DEFAULT_IMAGE
    p = args.prompt if args.prompt else DEFAULT_PROMPT
    try:
        out = generate_video(
            image_path=img,
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
