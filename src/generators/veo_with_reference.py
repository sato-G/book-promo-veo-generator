#!/usr/bin/env python3
"""
Veo 3.1 with reference image, prompt overrides, output naming.

Options:
  --prompt, --duration {4,6,8}, --aspect {16:9,9:16}, --resolution {720p,1080p}, --tag, --output, --image
"""

import os
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from google import genai
from google.genai import types


def main():
    ap = argparse.ArgumentParser(description="Veo 3.1 text-to-video with reference image")
    ap.add_argument("--prompt", type=str, help="Override generation prompt")
    ap.add_argument("--duration", type=int, default=8, help="Duration seconds (4/6/8)")
    ap.add_argument("--aspect", type=str, default="16:9", help="Aspect ratio (16:9 or 9:16)")
    ap.add_argument("--resolution", type=str, default="720p", help="Resolution (720p or 1080p)")
    ap.add_argument("--tag", type=str, help="Short tag for filename (e.g., mouthonly)")
    ap.add_argument("--output", type=str, help="Explicit output filepath (mp4)")
    ap.add_argument("--image", type=Path, required=True, help="Reference image path")
    args = ap.parse_args()

    if not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit("GOOGLE_API_KEY not set.")

    if not args.image.exists():
        raise SystemExit(f"Image not found: {args.image}")

    client = genai.Client()

    # Build Image payload from bytes
    mime = "image/png" if args.image.suffix.lower() == ".png" else "image/jpeg"
    ref_image = types.Image(imageBytes=args.image.read_bytes(), mimeType=mime)
    dress_reference = types.VideoGenerationReferenceImage(
        image=ref_image,
        referenceType=types.VideoGenerationReferenceType.ASSET,
    )

    negative = (
        "no identity change, no blinking, no eye movement, no head movement, no body sway, "
        "no hair movement, no camera shake, no flicker, no jitter, no added text, no graphics, "
        "no extra objects, no scene cuts"
    )

    cfg = types.GenerateVideosConfig(
        referenceImages=[dress_reference],
        durationSeconds=args.duration,
        aspectRatio=args.aspect,
        resolution=args.resolution,
        negativePrompt=negative,
    )

    prompt = args.prompt or (
        "Single talking-head shot guided by the provided reference image. "
        "Japanese voice-over, clear announcer style; 8 seconds; 16:9; clean neutral studio look."
    )

    print("🎥 Requesting Veo 3.1 generation with reference image…")
    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt,
        config=cfg,
    )

    while not operation.done:
        print("Waiting for video generation to complete…")
        time.sleep(10)
        operation = client.operations.get(operation)

    if not getattr(operation, 'response', None) or not getattr(operation.response, 'generated_videos', None):
        raise SystemExit("Video generation did not return a result. Try relaxing constraints in the prompt.")

    generated_video = operation.response.generated_videos[0]
    client.files.download(file=generated_video.video)

    out_dir = Path("data/output/veo_genai")
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        aspect_token = args.aspect.replace(":", "x")
        tag = (args.tag or "clip").strip()
        out_path = out_dir / f"veo3_ref_{tag}_{args.duration}s_{aspect_token}_{args.resolution}_{ts}.mp4"

    generated_video.video.save(str(out_path))
    print(f"Generated video saved to {out_path}")


if __name__ == "__main__":
    main()

