#!/usr/bin/env python3
"""
動画フレーム追加のテストスクリプト

既存の冒頭アニメーション動画にフレームを追加
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.generators.video_frame_generator import add_video_frame


def main():
    """テストメイン関数"""

    # 入力動画（冒頭アニメーション動画を使用）
    video_path = Path("data/output/opening_animation_test.mp4")

    # 表紙画像（『あの戦争は何だったのか』の表紙）
    cover_path = Path("data/『あの戦争は何だったのか』/images/AI用素材_1.jpg")

    # 出力パス
    output_path = Path("data/output/framed_video_test.mp4")

    # 書籍情報
    title = "『あの戦争は何だったのか』"
    author = "保阪正康 著"

    print("🎨 動画フレーム追加テスト")
    print(f"📹 入力動画: {video_path}")
    print(f"📸 表紙画像: {cover_path}")
    print(f"📖 タイトル: {title}")
    print(f"✍️  著者: {author}")
    print()

    # 動画が存在しない場合はエラー
    if not video_path.exists():
        print(f"❌ エラー: 入力動画が見つかりません: {video_path}")
        print(f"💡 先に冒頭アニメーションを生成してください:")
        print(f"   python src/simpletest/test_opening_animation.py")
        return

    # フレーム追加動画を生成
    result = add_video_frame(
        video_path=video_path,
        output_path=output_path,
        title=title,
        cover_image_path=cover_path,
        author=author,
        layout="top_bottom"
    )

    print(f"\n✅ テスト完了！")
    print(f"📂 生成された動画: {result}")


if __name__ == '__main__':
    main()
