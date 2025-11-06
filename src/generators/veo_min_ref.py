#!/usr/bin/env python3
"""
Minimal Veo 3.1 (google-genai) runner using a single or multiple reference images.

- Only sets referenceImages in GenerateVideosConfig
"""

import os
import time
from pathlib import Path
from datetime import datetime

from google import genai
from google.genai import types


def run_minimal_with_reference(
    image_path: Path,
    prompt: str,
    model: str = "veo-3.1-generate-preview",
    extra_refs: list[Path] | None = None,
) -> Path:
    if not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit("GOOGLE_API_KEY not set in environment.")

    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}")

    client = genai.Client()

    def make_ref(p: Path):
        mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
        img = types.Image(imageBytes=p.read_bytes(), mimeType=mime)
        return types.VideoGenerationReferenceImage(
            image=img,
            referenceType=types.VideoGenerationReferenceType.ASSET,
        )

    refs = [make_ref(image_path)]
    if extra_refs:
        for p in extra_refs:
            if p and p.exists():
                refs.append(make_ref(p))

    cfg = types.GenerateVideosConfig(referenceImages=refs)

    print("\n🎥 Veo 3.1 generate_videos (minimal, with reference image)…")
    operation = client.models.generate_videos(
        model=model,
        prompt=prompt,
        config=cfg,
    )

    while not operation.done:
        print("⏳ Generating… 10s wait")
        time.sleep(10)
        operation = client.operations.get(operation)

    if not getattr(operation, 'response', None) or not getattr(operation.response, 'generated_videos', None):
        raise SystemExit("No video returned. Try a simpler prompt or remove extra constraints.")

    vid = operation.response.generated_videos[0]
    client.files.download(file=vid.video)

    out_dir = Path("data/output/veo_genai")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out = out_dir / f"veo3_min_ref_{ts}.mp4"
    vid.video.save(str(out))
    print(f"✅ Saved: {out}")
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Minimal Veo 3.1 with reference image(s)")
    ap.add_argument("--image", required=True, type=Path, help="Primary reference image path")
    ap.add_argument("--extra-ref", action="append", type=Path, help="Additional reference image(s)")
    ap.add_argument("--prompt", required=False, type=str,
                    default=("Single cinematic shot guided by the provided reference image. "
                             "Neutral background, clean and sharp look. 8 seconds, 16:9."))
    args = ap.parse_args()

    run_minimal_with_reference(args.image, args.prompt, extra_refs=args.extra_ref or [])


if __name__ == "__main__":
    main()

