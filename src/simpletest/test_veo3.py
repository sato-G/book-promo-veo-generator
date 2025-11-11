#!/usr/bin/env python3
"""
Veo 3.1のシンプルテストスクリプト

使い方:
    cd src/simpletest
    python test_veo3.py
"""

import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.generators.veo3_sample import generate_video


# ========================================
# テスト設定（ここを編集）
# ========================================
TEST_IMAGE = (
    project_root
    / "/Users/sato/work/book-promo-veo-generator/data/image_sample/test1.jpg"
)  # テスト用画像パス
TEST_PROMPT = "本のタイトルが浮かび上がる"  # プロンプト
TEST_DURATION = 4  # 動画長さ（4, 6, 8秒）
OUTPUT_DIR = project_root / "data/output"  # 出力ディレクトリ
# ========================================


def main():
    print("\n" + "=" * 60)
    print("🧪 Veo 3.1 簡易テスト")
    print("=" * 60)
    print(f"画像: {TEST_IMAGE}")
    print(f"プロンプト: {TEST_PROMPT}")
    print(f"長さ: {TEST_DURATION}秒")
    print("=" * 60 + "\n")

    try:
        output_path = generate_video(
            image_path=TEST_IMAGE,
            prompt=TEST_PROMPT,
            duration=TEST_DURATION,
            output_dir=OUTPUT_DIR,
        )

        print("\n" + "=" * 60)
        print("✅ テスト成功！")
        print("=" * 60)
        print(f"動画: {output_path}")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ テスト失敗: {e}\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
