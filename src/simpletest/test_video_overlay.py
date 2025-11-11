#!/usr/bin/env python3
"""
動画オーバーレイのテストスクリプト

スライドショー動画に表紙画像をゆらゆらオーバーレイ
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.generators.video_overlay_generator import add_floating_overlay


def main():
    """テストメイン関数"""

    # 入力動画（スライドショー動画）
    video_path = Path("/Users/sato/work/book-promo-veo-generator/data/output/slideshow_1762879638.mp4")

    # オーバーレイ画像（表紙タイトル画像）
    overlay_path = Path("/Users/sato/work/book-promo-veo-generator/data/『あの戦争は何だったのか』/images/ano_title.jpg")

    # 出力パス
    output_path = Path("data/output/overlay_test.mp4")

    print("🎨 動画オーバーレイテスト")
    print(f"📹 入力動画: {video_path}")
    print(f"📸 オーバーレイ画像: {overlay_path}")
    print()

    # 動画が存在しない場合はエラー
    if not video_path.exists():
        print(f"❌ エラー: 入力動画が見つかりません: {video_path}")
        return

    if not overlay_path.exists():
        print(f"❌ エラー: オーバーレイ画像が見つかりません: {overlay_path}")
        return

    # オーバーレイ動画を生成（下部に静止した表紙、上下に白い余白）
    result = add_floating_overlay(
        video_path=video_path,
        output_path=output_path,
        overlay_image_path=overlay_path,
        position="bottom",
        overlay_scale=0.25,  # 動画の高さの25%（1/4）
        animation="static",  # 静止（アニメーションなし）
        video_scale=1.0,  # 動画を縮小しない（元のサイズ）
        background_color=(255, 255, 255),  # 白背景
        video_y_offset_override=-400,  # 動画を400px上にスライド（下に白い余白ができる）
        top_bar_height=350,  # 上部に350pxの白い帯を被せる
        subtitle_text="テスト字幕：これは上部白いエリアに表示されます"  # 字幕テキスト
    )

    print(f"\n✅ テスト完了！")
    print(f"📂 生成された動画: {result}")


if __name__ == '__main__':
    main()
