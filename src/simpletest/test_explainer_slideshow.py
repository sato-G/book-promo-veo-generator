#!/usr/bin/env python3
"""
Explainer Slideshow 簡易テスト

提供テキストを6枚構成（最後は書影）で動画化します。
"""

from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.generators.explainer_slideshow import generate_explainer


TEXT = (
    "ストレスでお腹が痛くなる/胃が重い背景には、脳から分泌されるCRHが関わります。"
    "CRHは受容体に結合して消化管の動きを調節します。"
    "受容体にはⅠ型とⅡ型があり、どこに多く発現しているかで反応が変わります。"
    "胃・十二指腸を支配する迷走神経にはⅡ型が発現し、CRHが結合すると胃の運動が抑制。"
    "結果として重だるさや消化不良、胃痛につながります。"
    "一方、結腸・大腸の蠕動を支配する副交感神経にはⅠ型が発現し、CRHが作用すると蠕動が促進。"
    "腹痛や下痢が起きやすくなります。"
    "CRHは体内時計の影響で朝に高く、朝ストレスが加わると分泌が一段と増えて症状が強くなりがち。"
    "過去のトラウマや不安があると分泌がさらに増えて悪循環になります。"
    "こうした違いは受容体の発現量や機能差でも個人差が生じます。"
    "詳しくは本書で解説。最後に書影をご覧ください。"
)


def main():
    images = [
        project_root / "data/image_sample/test1.jpg",  # 差し替え可
        project_root / "data/image_sample/test1.jpg",
        project_root / "data/image_sample/test1.jpg",
        project_root / "data/image_sample/test1.jpg",
        project_root / "data/image_sample/test1.jpg",
    ]
    cover = project_root / "data/『土と生命の46億年史』 /images/表紙.png"  # 書影差し替え可

    out = generate_explainer(
        text=TEXT,
        images=images,
        add_cover=cover,
        duration=75.0,
        enable_tts=True,
        output_dir=project_root / "data/output",
    )
    print(f"✅ 出力: {out}")


if __name__ == "__main__":
    main()

