#!/usr/bin/env python3
"""
Nanobana Image Generator Client (CLI-oriented)

nanobana/nanobanana 等のローカルCLIを呼び出して画像生成。
CLIが未設定・未導入の場合は、プレースホルダー画像を生成してパイプラインを通せます。

使い方の例（CLI テンプレート指定）:

  export NANOBANA_CMD="nanobana --prompt '{prompt}' --out '{out}' --size 1080x1920"

  from nanobana_client import NanobanaClient
  client = NanobanaClient()
  paths = client.generate_images(["脳と腸の関係の抽象図"], out_dir=Path('data/generated'))
"""

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import List, Optional

from PIL import Image, ImageDraw, ImageFont


class NanobanaClient:
    def __init__(self, cmd_template: Optional[str] = None, fallback_placeholder: bool = True):
        self.cmd_template = cmd_template or os.getenv("NANOBANA_CMD")
        self.fallback_placeholder = fallback_placeholder

    def _run_cli(self, prompt: str, out_path: Path) -> bool:
        if not self.cmd_template:
            return False
        try:
            cmd = self.cmd_template.format(prompt=prompt.replace("'", "\'"), out=str(out_path))
            # shlex.splitで分割し、サブプロセス実行
            result = subprocess.run(shlex.split(cmd), capture_output=True, text=True)
            if result.returncode != 0:
                print(f"[nanobana] CLI error: {result.stderr.strip()}")
                return False
            return True
        except Exception as e:
            print(f"[nanobana] CLI invoke failed: {e}")
            return False

    def _make_placeholder(self, out_path: Path, text: str, size=(1080, 1920)) -> None:
        img = Image.new("RGB", size, (28, 28, 36))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 48)
        except Exception:
            font = ImageFont.load_default()
        # テキストを折り返し簡易描画（先頭150文字程度）
        snippet = (text or "").strip().replace("\n", " ")[:150]
        lines = []
        buf = ""
        max_w = int(size[0] * 0.8)
        for ch in snippet:
            test = buf + ch
            box = draw.textbbox((0, 0), test, font=font)
            if box[2] - box[0] > max_w:
                lines.append(buf)
                buf = ch
            else:
                buf = test
        if buf:
            lines.append(buf)

        y = int(size[1] * 0.1)
        for line in lines[:10]:
            box = draw.textbbox((0, 0), line, font=font)
            x = (size[0] - (box[2] - box[0])) // 2
            # 影
            draw.text((x+2, y+2), line, font=font, fill=(0, 0, 0))
            draw.text((x, y), line, font=font, fill=(230, 230, 240))
            y += (box[3] - box[1]) + 10
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path)

    def generate_images(self, prompts: List[str], out_dir: Path) -> List[Path]:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        outputs: List[Path] = []
        for i, prompt in enumerate(prompts, 1):
            out = out_dir / f"nanobana_slide_{i:02d}.png"
            ok = self._run_cli(prompt, out)
            if not ok:
                if not self.fallback_placeholder:
                    raise RuntimeError("Nanobana CLI not available and fallback disabled")
                self._make_placeholder(out, prompt)
            outputs.append(out)
        return outputs


def main():
    import argparse
    p = argparse.ArgumentParser(description="Nanobana Image Generator")
    p.add_argument("--prompt", action="append", help="画像プロンプト（複数可）")
    p.add_argument("--out-dir", type=Path, default=Path("data/generated/nanobana"))
    p.add_argument("--no-fallback", action="store_true")
    args = p.parse_args()

    client = NanobanaClient(fallback_placeholder=not args.no_fallback)
    paths = client.generate_images(args.prompt or ["テスト画像"], args.out_dir)
    print("\n".join(str(p) for p in paths))


if __name__ == "__main__":
    main()

