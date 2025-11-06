#!/usr/bin/env python3
"""
Make a video that uses a still image "as-is" (no generative changes).

Features
- Pads to target size/aspect without cropping (letterbox/pillarbox)
- Optional gentle Ken Burns zoom
- Writes H.264 + AAC ready-to-share MP4

Usage
  python image_to_clip.py \
    --image "path/to/image.jpg" \
    --out out.mp4 \
    --duration 8 \
    --size 1920x1080 \
    --fps 30 \
    --zoom 0.06     # optional, 6% slow push-in
"""

from pathlib import Path
import subprocess
import argparse


def build_filter(w: int, h: int, fps: int, duration: int, zoom: float | None) -> str:
    base = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,fps={fps}"
    if zoom and zoom > 0:
        # Total frames for zoom progression
        frames = fps * duration
        # Progress from 1.0 to (1+zoom)
        zp = (
            "zoompan="
            f"z='min(1+{zoom}*(on/{frames}),1+{zoom})':"
            "x='iw/2-(iw/2)/zoom':y='ih/2-(ih/2)/zoom':"
            f"d=1:s={w}x{h}"
        )
        return f"{base},{zp}"
    return base


def image_to_clip(image: Path, out: Path, duration: int = 8, size: str = "1920x1080", fps: int = 30, zoom: float | None = None):
    if not image.exists():
        raise SystemExit(f"Image not found: {image}")

    out.parent.mkdir(parents=True, exist_ok=True)

    try:
        w_str, h_str = size.lower().split("x", 1)
        w, h = int(w_str), int(h_str)
    except Exception:
        raise SystemExit("--size must be like 1920x1080 or 1080x1920")

    vf = build_filter(w, h, fps, duration, zoom)

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-t", str(duration),
        "-i", str(image),
        "-filter_complex", vf,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-r", str(fps),
        str(out),
    ]

    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser(description="Image → Video (as-is, non-generative)")
    ap.add_argument("--image", required=True, type=Path, help="Input still image path")
    ap.add_argument("--out", required=True, type=Path, help="Output MP4 path")
    ap.add_argument("--duration", type=int, default=8, help="Seconds (default 8)")
    ap.add_argument("--size", type=str, default="1920x1080", help="Frame size WxH (default 1920x1080)")
    ap.add_argument("--fps", type=int, default=30, help="Frames per second (default 30)")
    ap.add_argument("--zoom", type=float, help="Optional slow push-in percent as decimal e.g. 0.06")
    args = ap.parse_args()

    image_to_clip(args.image, args.out, args.duration, args.size, args.fps, args.zoom)


if __name__ == "__main__":
    main()

