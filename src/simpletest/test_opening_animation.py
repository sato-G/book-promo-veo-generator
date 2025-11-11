#!/usr/bin/env python3
"""
冒頭アニメーション生成のテストスクリプト

『あの戦争は何だったのか』を使ってテスト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.generators.opening_animation_generator import generate_opening_animation


def main():
    """テストメイン関数"""

    # 入力画像（『あの戦争は何だったのか』の表紙）
    image_path = Path("data/『あの戦争は何だったのか』/images/AI用素材_1.jpg")

    # キャッチコピー（amazon.txtから）
    catchphrase = "日本はどこで間違えたのか?"

    # 出力パス
    output_path = Path("data/output/opening_animation_test.mp4")

    print("🎬 冒頭アニメーション生成テスト")
    print(f"📸 入力画像: {image_path}")
    print(f"💬 キャッチコピー: {catchphrase}")
    print()

    # 動画生成（字幕 + ナレーション付き）
    result = generate_opening_animation(
        image_path=image_path,
        output_path=output_path,
        catchphrase=catchphrase,
        duration=2.0,  # 合計2秒（0.2秒アニメ + 1.8秒停止）
        animation_duration=0.2,  # アニメーション部分（0.2秒で回転ズーム）
        zoom_start=2.5,  # 2.5倍からスタート（より劇的）
        zoom_end=1.0,
        enable_tts=True  # TTSナレーションを有効化
    )

    print(f"\n✅ テスト完了！")
    print(f"📂 生成された動画: {result}")


if __name__ == '__main__':
    main()
