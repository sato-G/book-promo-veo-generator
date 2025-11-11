#!/usr/bin/env python3
"""
Simple Video Concatenator

複数の動画を指定順でそのまま連結して1本のMP4にします。

使い方:
  python -m src.generators.video_concat \
    --inputs data/output/part1.mp4 data/output/part2.mp4 data/output/part3.mp4 \
    --output data/output/merged.mp4

オプション:
  --fps 24             出力FPS（未指定時は最初の動画のfps/なければ24）
  --resolution 1080x1920  出力解像度を固定リサイズ（省略可）
  --method compose      連結方法（moviepyのcomposeを既定）
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional, Tuple

from moviepy import VideoFileClip, concatenate_videoclips


def parse_resolution(s: Optional[str]) -> Optional[Tuple[int, int]]:
    if not s:
        return None
    try:
        w, h = s.lower().split("x")
        return int(w), int(h)
    except Exception:
        raise ValueError("--resolution は 1080x1920 の形式で指定してください")


def concat_videos(
    inputs: List[Path],
    output: Path,
    *,
    fps: Optional[int] = None,
    resolution: Optional[Tuple[int, int]] = None,
    method: str = "compose",
) -> Path:
    if len(inputs) < 2:
        raise ValueError("少なくとも2ファイル以上の入力が必要です")

    clips = []
    inferred_fps = None
    try:
        for p in inputs:
            clip = VideoFileClip(str(p))
            # シンプル方針: リサイズしない（composeで自動調整に任せる）
            clips.append(clip)
            if inferred_fps is None and getattr(clip, "fps", None):
                inferred_fps = int(round(clip.fps))

        out_fps = fps or inferred_fps or 24

        final = concatenate_videoclips(clips, method=method)
        output.parent.mkdir(parents=True, exist_ok=True)
        final.write_videofile(
            str(output),
            fps=out_fps,
            codec="libx264",
            audio_codec="aac",
            preset="medium",
            bitrate="5000k",
        )
        return output
    finally:
        for c in clips:
            try:
                c.close()
            except Exception:
                pass


def main():
    import argparse

    p = argparse.ArgumentParser(description="Concatenate videos in order")
    p.add_argument("--inputs", nargs="+", type=Path, required=True, help="入力動画のパス（複数）")
    p.add_argument("--output", type=Path, required=True, help="出力先MP4")
    p.add_argument("--fps", type=int, help="出力FPS（未指定時は入力から推定）")
    p.add_argument("--resolution", type=str, help="固定リサイズ（例: 1080x1920）")
    p.add_argument("--method", type=str, default="compose", choices=["compose", "chain"], help="連結方法")
    args = p.parse_args()

    try:
        res = parse_resolution(args.resolution)
        out = concat_videos(
            inputs=args.inputs,
            output=args.output,
            fps=args.fps,
            resolution=res,
            method=args.method,
        )
        print(f"✅ 出力: {out}")
    except Exception as e:
        print(f"❌ エラー: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
