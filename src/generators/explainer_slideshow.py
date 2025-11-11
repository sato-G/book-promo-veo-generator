#!/usr/bin/env python3
"""
Explainer Slideshow Generator

長文テキストを画像枚数に合わせて分割し、字幕・TTS付きスライドショー動画を生成。
最後に書影（カバー）を配置するワークフローを簡単に実行できます。

既存の `generate_slideshow` をラップして、
- テキスト分割（句読点優先、足りなければ読点で細分化）
- 画像枚数に合わせて必ず分割数を調整
- 均等割りのタイミングを付与（TTS有効時は実長に同期）
をまとめて行います。
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Optional, Tuple
import argparse
import time
import re

from .slideshow_generator import generate_slideshow


def split_text_for_images(text: str, num_images: int) -> List[str]:
    """画像枚数に合わせてテキストを自然に分割（句読点→読点→調整）"""
    text_clean = text.replace("\r", "").strip()
    # 句点で1文ずつ（全角/半角）
    sentences = re.split(r'([。！？\?])', text_clean)
    segments: List[str] = []
    i = 0
    while i < len(sentences):
        if i + 1 < len(sentences) and sentences[i+1] in '。！？?':
            segments.append((sentences[i] + sentences[i+1]).strip())
            i += 2
        else:
            if sentences[i].strip():
                segments.append(sentences[i].strip())
            i += 1
    segments = [s for s in segments if s]

    # 足りなければ読点で細分化
    if len(segments) < num_images:
        new_segments: List[str] = []
        for seg in segments:
            parts = re.split(r'(、)', seg)
            buf: List[str] = []
            j = 0
            while j < len(parts):
                if j + 1 < len(parts) and parts[j+1] == '、':
                    buf.append((parts[j] + parts[j+1]).strip())
                    j += 2
                else:
                    if parts[j].strip():
                        buf.append(parts[j].strip())
                    j += 1
            new_segments.extend([s for s in buf if s])
        if new_segments:
            segments = new_segments

    # さらに調整して必ず画像枚数に合わせる
    if not segments:
        segments = ["..."]

    if len(segments) < num_images:
        # 最長を2分割して水増し
        while len(segments) < num_images:
            idx = max(range(len(segments)), key=lambda k: len(segments[k]))
            s = segments[idx]
            if len(s) <= 1:
                segments.append("...")
                continue
            mid = len(s) // 2
            segments[idx] = s[:mid]
            segments.insert(idx + 1, s[mid:])
    elif len(segments) > num_images:
        # 均等に結合して減らす
        step = len(segments) / num_images
        merged: List[str] = []
        for k in range(num_images):
            start = int(k * step)
            end = int((k + 1) * step)
            if end <= start:
                end = start + 1
            merged.append("".join(segments[start:end]).strip())
        segments = [s if s else "..." for s in merged]

    return segments[:num_images]


def build_narration_segments(text: str, num_images: int, duration: float) -> List[Dict]:
    """画像枚数に合うセグメントと均等時間を付与"""
    segs = split_text_for_images(text, num_images)
    if num_images <= 0:
        raise ValueError("num_images must be > 0")
    seg_duration = max(0.5, duration / num_images)
    segments: List[Dict] = []
    t = 0.0
    for s in segs:
        segments.append({"text": s, "start": t, "duration": seg_duration})
        t += seg_duration
    return segments


def generate_explainer(
    *,
    text: str,
    images: List[Path],
    output_dir: Path = Path("data/output"),
    duration: float = 75.0,
    resolution: Tuple[int, int] = (1080, 1920),
    add_cover: Optional[Path] = None,
    enable_tts: bool = True,
    final_title: Optional[str] = None,
) -> Path:
    """長文テキスト + 複数画像（最後に書影）で解説スライドショーを生成"""
    imgs = [Path(p) for p in images]
    if add_cover:
        imgs.append(Path(add_cover))
    if len(imgs) < 2:
        raise ValueError("画像は2枚以上を推奨（最後を表紙に）")

    # 出力ファイル
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    out = output_dir / f"explainer_{ts}.mp4"

    # セグメント作成（均等割）
    narration_segments = build_narration_segments(text, len(imgs), duration)
    # 最終スライド（カバー）にタイトル字幕を重ねたい場合
    if add_cover and final_title and narration_segments:
        narration_segments[-1]["text"] = final_title

    # 生成（TTS有効時は実長に同期）
    return generate_slideshow(
        image_paths=imgs,
        output_path=out,
        narration_segments=narration_segments,
        bgm_path=None,
        duration=duration,
        resolution=resolution,
        transition_advance=0.2,
        pan_enabled=True,
        pan_scale=1.12,
        enable_tts=enable_tts,
    )


def _read_text_file(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description="Explainer Slideshow Generator")
    p.add_argument("--text-file", type=Path, help="説明テキスト（UTF-8）")
    p.add_argument("--image", type=Path, action="append", help="画像（複数指定可、最後は書影に）")
    p.add_argument("--cover", type=Path, help="書影（最後に追加）")
    p.add_argument("--duration", type=float, default=75.0, help="動画の長さ（秒）")
    p.add_argument("--no-tts", action="store_true", help="TTS無効（字幕のみ）")
    p.add_argument("--output-dir", type=Path, default=Path("data/output"))
    p.add_argument("--final-title", type=str, help="最終スライド（書影）に重ねるタイトル字幕")
    args = p.parse_args()

    if not args.text_file or not args.image:
        raise SystemExit("--text-file と --image は必須です（--imageは複数可）")

    text = _read_text_file(args.text_file)
    images = args.image
    out = generate_explainer(
        text=text,
        images=images,
        output_dir=args.output_dir,
        duration=args.duration,
        add_cover=args.cover,
        enable_tts=not args.no_tts,
        final_title=args.final_title,
    )
    print(f"✅ 出力: {out}")


if __name__ == "__main__":
    main()
