#!/usr/bin/env python3
"""
End-to-End: Nanobana 画像生成 → Explainer スライドショー合成

1) テキストをスライド数に分割
2) セグメントごとに画像プロンプトを作成（そのまま or 前置きテンプレ）
3) nanobana(na) CLI で画像生成（未設定時はプレースホルダー）
4) 最後に書影（カバー）を追加し、タイトルは最終セグメント字幕に表示
5) explainer_slideshow で字幕/TTS付き動画に合成
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import List, Optional

from .nanobana_client import NanobanaClient
from .explainer_slideshow import split_text_for_images, generate_explainer


def build_explainer_pipeline(
    *,
    text: str,
    slides: int,
    prompt_prefix: Optional[str] = None,
    cover_path: Optional[Path] = None,
    book_title: Optional[str] = None,
    out_dir: Path = Path("data/output"),
    enable_tts: bool = True,
    duration: float = 75.0,
) -> Path:
    # 1) セグメント化
    segs = split_text_for_images(text, slides + (1 if cover_path else 0))

    # 最後がカバーなら、最終セグメントをタイトル字幕に置き換える
    if cover_path and book_title:
        segs[-1] = f"『{book_title}』"

    # 2) 画像プロンプト作成（最後がカバーのときは画像を生成しない）
    content_segs = segs[:-1] if cover_path else segs
    prompts: List[str] = []
    for s in content_segs:
        base = s.replace("\n", " ").strip()
        if prompt_prefix:
            prompts.append(f"{prompt_prefix} {base}")
        else:
            prompts.append(base)

    # 3) 画像生成
    ts = int(time.time())
    gen_dir = Path("data/generated/nanobana") / str(ts)
    client = NanobanaClient()
    image_paths = client.generate_images(prompts, out_dir=gen_dir)

    # 4) カバー追加
    final_cover = Path(cover_path) if cover_path else None

    # 5) 合成
    out = generate_explainer(
        text="\n".join(segs),
        images=image_paths,
        add_cover=final_cover,
        output_dir=out_dir,
        duration=duration,
        enable_tts=enable_tts,
    )
    return out


def main():
    import argparse
    p = argparse.ArgumentParser(description="Nanobana→Explainer パイプライン")
    p.add_argument("--text-file", type=Path, required=True)
    p.add_argument("--slides", type=int, default=5)
    p.add_argument("--prompt-prefix", type=str, help="画像生成の前置きテンプレ（任意）")
    p.add_argument("--cover", type=Path, help="最後の書影")
    p.add_argument("--title", type=str, help="書影と一緒に字幕で表示するタイトル")
    p.add_argument("--duration", type=float, default=75.0)
    p.add_argument("--no-tts", action="store_true")
    p.add_argument("--out-dir", type=Path, default=Path("data/output"))
    args = p.parse_args()

    text = Path(args.text_file).read_text(encoding="utf-8")
    out = build_explainer_pipeline(
        text=text,
        slides=args.slides,
        prompt_prefix=args.prompt_prefix,
        cover_path=args.cover,
        book_title=args.title,
        out_dir=args.out_dir,
        enable_tts=not args.no_tts,
        duration=args.duration,
    )
    print(f"✅ 出力: {out}")


if __name__ == "__main__":
    main()

