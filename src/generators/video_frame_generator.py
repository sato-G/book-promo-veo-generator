#!/usr/bin/env python3
"""
動画フレーム追加モジュール

書籍プロモーション動画の周囲にブランディング要素を追加
タイトル、表紙画像などを配置してプロフェッショナルな仕上がりに
"""

from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy import VideoFileClip, VideoClip


def add_video_frame(
    video_path: Path,
    output_path: Path,
    title: str,
    cover_image_path: Optional[Path] = None,
    author: Optional[str] = None,
    layout: str = "top_bottom",
    resolution: Tuple[int, int] = (1080, 1920),
    background_color: Tuple[int, int, int] = (20, 20, 30),
    fps: Optional[int] = None
) -> Path:
    """
    動画の周囲にブランディング要素を追加したフレーム動画を生成

    Args:
        video_path: 入力動画パス
        output_path: 出力動画パス
        title: タイトルテキスト
        cover_image_path: 表紙画像パス（オプション）
        author: 著者名（オプション）
        layout: レイアウトパターン（"top_bottom" または "left_right"）
        resolution: 出力解像度 (width, height)
        background_color: 背景色 (R, G, B)
        fps: フレームレート（Noneの場合は元動画のfpsを使用）

    Returns:
        出力動画のパス
    """
    print("=" * 60)
    print("🎨 動画フレーム追加開始")
    print("=" * 60)
    print(f"📹 入力動画: {video_path}")
    print(f"📖 タイトル: {title}")
    if cover_image_path:
        print(f"📸 表紙画像: {cover_image_path}")
    if author:
        print(f"✍️  著者: {author}")
    print(f"📐 レイアウト: {layout}")
    print(f"📐 解像度: {resolution[0]}x{resolution[1]}")
    print("=" * 60 + "\n")

    # 出力ディレクトリを作成
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ==========================================
    # 1. 入力動画を読み込む
    # ==========================================
    print("【1】入力動画を読み込み中...")
    video_clip = VideoFileClip(str(video_path))
    video_duration = video_clip.duration
    video_fps = fps if fps else video_clip.fps
    print(f"✓ 動画読み込み完了: {video_duration:.2f}秒, {video_fps}fps")

    # ==========================================
    # 2. フレーム画像を作成（タイトル + 表紙）
    # ==========================================
    print("\n【2】フレーム要素を作成中...")

    target_w, target_h = resolution

    if layout == "top_bottom":
        # パターンA: 上下配置
        # 高さ配分: タイトル 150px / 動画 1200px / 表紙 570px
        title_height = 150
        video_height = 1200
        cover_height = 570

        # 動画の配置サイズを計算（アスペクト比を保つ）
        video_w, video_h = video_clip.size
        video_aspect = video_w / video_h

        # 動画エリアの幅いっぱいに配置
        display_video_w = target_w
        display_video_h = int(display_video_w / video_aspect)

        # 高さが収まらない場合は高さ基準に調整
        if display_video_h > video_height:
            display_video_h = video_height
            display_video_w = int(display_video_h * video_aspect)

        print(f"   動画表示サイズ: {display_video_w}x{display_video_h}")

    elif layout == "left_right":
        # パターンB: 左右配置（将来の拡張用）
        raise NotImplementedError("left_right layout は未実装です")
    else:
        raise ValueError(f"Unknown layout: {layout}")

    # ==========================================
    # 3. 各フレーム用の静的要素を作成
    # ==========================================
    print("\n【3】静的要素（タイトル、表紙）を作成中...")

    # 背景キャンバスを作成
    frame_image = Image.new('RGB', resolution, background_color)
    draw = ImageDraw.Draw(frame_image)

    # タイトル部分を描画
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 60)
    except:
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 60)
        except:
            title_font = ImageFont.load_default()

    # タイトルを描画（上部中央）
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (target_w - title_w) // 2
    title_y = (title_height - (title_bbox[3] - title_bbox[1])) // 2

    # タイトルの影
    for offset_x in range(-3, 4):
        for offset_y in range(-3, 4):
            if offset_x != 0 or offset_y != 0:
                draw.text((title_x + offset_x, title_y + offset_y), title, font=title_font, fill=(0, 0, 0))

    # タイトル本体（白）
    draw.text((title_x, title_y), title, font=title_font, fill=(255, 255, 255))
    print(f"   ✓ タイトル描画完了: {title}")

    # 表紙画像を配置（下部）
    if cover_image_path and cover_image_path.exists():
        cover_img = Image.open(cover_image_path)

        # 表紙エリアに収まるようにリサイズ
        cover_area_h = cover_height - 40  # 上下に20pxずつマージン
        cover_w, cover_h = cover_img.size
        cover_aspect = cover_w / cover_h

        # 高さ基準でリサイズ
        display_cover_h = cover_area_h
        display_cover_w = int(display_cover_h * cover_aspect)

        # 幅が収まらない場合は幅基準に調整
        if display_cover_w > target_w - 40:
            display_cover_w = target_w - 40
            display_cover_h = int(display_cover_w / cover_aspect)

        cover_resized = cover_img.resize((display_cover_w, display_cover_h), Image.Resampling.LANCZOS)

        # 表紙を下部中央に配置
        cover_x = (target_w - display_cover_w) // 2
        cover_y = title_height + video_height + (cover_height - display_cover_h) // 2

        frame_image.paste(cover_resized, (cover_x, cover_y))
        print(f"   ✓ 表紙画像配置完了: {display_cover_w}x{display_cover_h}")

        # 著者名を表紙の下に配置
        if author:
            try:
                author_font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 36)
            except:
                author_font = ImageFont.load_default()

            draw = ImageDraw.Draw(frame_image)
            author_bbox = draw.textbbox((0, 0), author, font=author_font)
            author_w = author_bbox[2] - author_bbox[0]
            author_x = (target_w - author_w) // 2
            author_y = cover_y + display_cover_h + 10

            # 著者名の影
            for offset_x in range(-2, 3):
                for offset_y in range(-2, 3):
                    if offset_x != 0 or offset_y != 0:
                        draw.text((author_x + offset_x, author_y + offset_y), author, font=author_font, fill=(0, 0, 0))

            # 著者名本体（白）
            draw.text((author_x, author_y), author, font=author_font, fill=(200, 200, 200))
            print(f"   ✓ 著者名描画完了: {author}")

    # 静的フレーム画像をnumpy配列に変換
    frame_array = np.array(frame_image)

    # ==========================================
    # 4. 動画を合成したフレームを生成
    # ==========================================
    print("\n【4】動画を合成中...")

    # 動画の配置位置を計算
    video_x = (target_w - display_video_w) // 2
    video_y = title_height + (video_height - display_video_h) // 2

    def make_frame(t):
        """時間tに応じたフレームを生成（静的フレーム + 動画）"""
        # 静的フレームをコピー
        frame = frame_array.copy()

        # 動画のフレームを取得
        video_frame = video_clip.get_frame(t)

        # 動画フレームをリサイズ
        video_frame_img = Image.fromarray(video_frame).resize(
            (display_video_w, display_video_h),
            Image.Resampling.LANCZOS
        )
        video_frame_resized = np.array(video_frame_img)

        # 動画を中央エリアに配置
        frame[video_y:video_y+display_video_h, video_x:video_x+display_video_w] = video_frame_resized

        return frame

    # カスタムクリップを作成
    final_clip = VideoClip(make_frame, duration=video_duration).with_fps(video_fps)

    # 元動画の音声を追加
    if video_clip.audio:
        final_clip = final_clip.with_audio(video_clip.audio)
        print("✓ 音声を引き継ぎました")

    print(f"✓ フレーム合成完了")

    # ==========================================
    # 5. 動画を出力
    # ==========================================
    print("\n【5】動画を出力中...")
    final_clip.write_videofile(
        str(output_path),
        fps=video_fps,
        codec='libx264',
        audio=(video_clip.audio is not None),
        preset='medium',
        threads=4
    )

    # クリップを閉じる
    video_clip.close()
    final_clip.close()

    print("\n" + "=" * 60)
    print("✅ 動画フレーム追加完了！")
    print("=" * 60)
    print(f"📂 出力先: {output_path}")
    print(f"⏱️  動画の長さ: {video_duration:.2f}秒")
    print(f"📐 解像度: {resolution[0]}x{resolution[1]}")
    print(f"🎬 フレームレート: {video_fps}fps")
    print(f"📖 タイトル: {title}")
    if cover_image_path:
        print(f"📸 表紙: あり")
    print("=" * 60)

    return output_path


def main():
    """CLI実行用のメイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='動画にフレームを追加')
    parser.add_argument('--video', '-v', type=str, required=True,
                       help='入力動画パス')
    parser.add_argument('--output', '-o', type=str, required=True,
                       help='出力動画パス')
    parser.add_argument('--title', '-t', type=str, required=True,
                       help='タイトルテキスト')
    parser.add_argument('--cover', '-c', type=str, default=None,
                       help='表紙画像パス')
    parser.add_argument('--author', '-a', type=str, default=None,
                       help='著者名')
    parser.add_argument('--layout', '-l', type=str, default='top_bottom',
                       choices=['top_bottom', 'left_right'],
                       help='レイアウトパターン')

    args = parser.parse_args()

    cover_path = Path(args.cover) if args.cover else None

    add_video_frame(
        video_path=Path(args.video),
        output_path=Path(args.output),
        title=args.title,
        cover_image_path=cover_path,
        author=args.author,
        layout=args.layout
    )


if __name__ == '__main__':
    main()
