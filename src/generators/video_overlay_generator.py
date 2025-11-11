#!/usr/bin/env python3
"""
動画オーバーレイ生成モジュール

動画の上に表紙画像などをオーバーレイして、アニメーション効果を追加
"""

from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import numpy as np
from moviepy import VideoFileClip, VideoClip, CompositeVideoClip, ImageClip
import math


def add_floating_overlay(
    video_path: Path,
    output_path: Path,
    overlay_image_path: Path,
    position: str = "bottom",
    overlay_scale: float = 0.25,
    animation: str = "float",
    video_scale: float = 0.5,
    background_color: Tuple[int, int, int] = (255, 255, 255),
    video_y_offset_override: Optional[int] = None,
    top_bar_height: int = 0,
    subtitle_text: Optional[str] = None,
    fps: Optional[int] = None
) -> Path:
    """
    動画を縮小して上下に白い余白を作り、画像をオーバーレイ（出力サイズは元動画と同じ）

    Args:
        video_path: 入力動画パス
        output_path: 出力動画パス
        overlay_image_path: オーバーレイする画像パス
        position: オーバーレイ位置（"bottom", "top", "left", "right", "center"）
        overlay_scale: オーバーレイ画像のサイズ（元動画の高さに対する割合）
        animation: アニメーション種類（"float": ゆらゆら、"static": 静止）
        video_scale: 動画の縮小率（例: 0.5 = 50%、上下に25%ずつの余白）
        background_color: 背景色 (R, G, B) デフォルトは白
        video_y_offset_override: 動画のY座標を直接指定（Noneの場合は自動計算）
        top_bar_height: 上部に被せる白い帯の高さ（ピクセル）
        subtitle_text: 上部白いエリアに表示する字幕テキスト（オプション）
        fps: フレームレート（Noneの場合は元動画のfpsを使用）

    Returns:
        出力動画のパス
    """
    print("=" * 60)
    print("🎨 動画オーバーレイ追加開始")
    print("=" * 60)
    print(f"📹 入力動画: {video_path}")
    print(f"📸 オーバーレイ画像: {overlay_image_path}")
    print(f"📍 配置位置: {position}")
    print(f"📏 オーバーレイサイズ: {overlay_scale * 100:.1f}%")
    print(f"✨ アニメーション: {animation}")
    print(f"📐 動画縮小率: {video_scale * 100:.1f}%")
    print(f"🎨 背景色: RGB{background_color}")
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
    video_w, video_h = video_clip.size
    print(f"✓ 動画読み込み完了: {video_w}x{video_h}, {video_duration:.2f}秒, {video_fps}fps")

    # 出力サイズは元動画と同じ
    canvas_w = video_w
    canvas_h = video_h

    # 動画を縮小
    scaled_video_w = int(video_w * video_scale)
    scaled_video_h = int(video_h * video_scale)

    # 余白サイズを計算
    margin_top = (video_h - scaled_video_h) // 2
    margin_bottom = video_h - scaled_video_h - margin_top

    # 動画の配置位置（Y座標）
    if video_y_offset_override is not None:
        video_y_offset = video_y_offset_override
        # オーバーライドの場合は余白を再計算
        if video_y_offset < 0:
            margin_top = 0
            margin_bottom = video_h - scaled_video_h + abs(video_y_offset)
        else:
            margin_top = video_y_offset
            margin_bottom = video_h - scaled_video_h - video_y_offset
    else:
        video_y_offset = margin_top

    print(f"✓ 出力サイズ: {canvas_w}x{canvas_h} (元動画と同じ)")
    print(f"✓ 縮小後の動画: {scaled_video_w}x{scaled_video_h}")
    print(f"✓ 動画のY座標: {video_y_offset}px")
    print(f"✓ 余白: 上{margin_top}px / 下{margin_bottom}px")
    if top_bar_height > 0:
        print(f"✓ 上部白い帯: {top_bar_height}px")

    # ==========================================
    # 2. オーバーレイ画像を読み込んでリサイズ
    # ==========================================
    print("\n【2】オーバーレイ画像を準備中...")
    overlay_img = Image.open(overlay_image_path)

    # オーバーレイサイズを計算（動画の高さに対する割合で）
    overlay_target_h = int(video_h * overlay_scale)
    overlay_w, overlay_h = overlay_img.size
    overlay_aspect = overlay_w / overlay_h

    overlay_display_h = overlay_target_h
    overlay_display_w = int(overlay_display_h * overlay_aspect)

    # 幅が動画よりはみ出る場合は幅基準に調整
    if overlay_display_w > video_w * 0.9:  # 動画幅の90%まで
        overlay_display_w = int(video_w * 0.9)
        overlay_display_h = int(overlay_display_w / overlay_aspect)

    overlay_resized = overlay_img.resize(
        (overlay_display_w, overlay_display_h),
        Image.Resampling.LANCZOS
    )
    print(f"✓ オーバーレイ画像リサイズ完了: {overlay_display_w}x{overlay_display_h}")

    # ==========================================
    # 3. アニメーション付きオーバーレイを作成
    # ==========================================
    print("\n【3】アニメーション付きオーバーレイを作成中...")

    # 基準位置を計算（キャンバス全体での位置）
    if position == "bottom":
        # 下部の白い余白エリア中央
        base_x = (canvas_w - overlay_display_w) // 2
        base_y = scaled_video_h + video_y_offset + (margin_bottom - overlay_display_h) // 2
    elif position == "top":
        # 上部の白い余白エリア中央
        base_x = (canvas_w - overlay_display_w) // 2
        base_y = (margin_top - overlay_display_h) // 2
    elif position == "center":
        # 中央（動画の中央）
        base_x = (canvas_w - overlay_display_w) // 2
        base_y = video_y_offset + (scaled_video_h - overlay_display_h) // 2
    elif position == "left":
        # 左中央（動画の左中央）
        base_x = 20
        base_y = video_y_offset + (scaled_video_h - overlay_display_h) // 2
    elif position == "right":
        # 右中央（動画の右中央）
        base_x = canvas_w - overlay_display_w - 20
        base_y = video_y_offset + (scaled_video_h - overlay_display_h) // 2
    else:
        raise ValueError(f"Unknown position: {position}")

    # オーバーレイ画像をnumpy配列に変換（RGBA対応）
    if overlay_resized.mode != 'RGBA':
        overlay_resized = overlay_resized.convert('RGBA')
    overlay_array = np.array(overlay_resized)

    def make_overlay_frame(t):
        """時間tに応じたオーバーレイフレームを生成"""
        if animation == "float":
            # ゆらゆらアニメーション
            # 周期を変えた複数の正弦波を組み合わせて自然な動きに
            float_x = math.sin(t * 1.2) * 15 + math.sin(t * 0.7) * 8  # 横方向の揺れ
            float_y = math.cos(t * 1.5) * 10 + math.cos(t * 0.9) * 5  # 縦方向の揺れ

            # 位置を計算
            current_x = base_x + float_x
            current_y = base_y + float_y

            # わずかな拡大縮小
            scale_factor = 1.0 + math.sin(t * 0.8) * 0.02  # ±2%の拡大縮小

            # スケール適用
            scaled_w = int(overlay_display_w * scale_factor)
            scaled_h = int(overlay_display_h * scale_factor)

            # リサイズ
            scaled_img = Image.fromarray(overlay_array).resize(
                (scaled_w, scaled_h),
                Image.Resampling.LANCZOS
            )

            # わずかな回転（±3度）
            rotation = math.sin(t * 0.6) * 3
            rotated_img = scaled_img.rotate(
                rotation,
                resample=Image.Resampling.BICUBIC,
                expand=False
            )

            return np.array(rotated_img)
        else:
            # 静止（アニメーションなし）
            return overlay_array

    # オーバーレイクリップを作成
    overlay_clip = VideoClip(make_overlay_frame, duration=video_duration).with_fps(video_fps)

    # 位置を設定する関数（アニメーションに合わせて位置を変更）
    def overlay_position(t):
        if animation == "float":
            float_x = math.sin(t * 1.2) * 15 + math.sin(t * 0.7) * 8
            float_y = math.cos(t * 1.5) * 10 + math.cos(t * 0.9) * 5
            scale_factor = 1.0 + math.sin(t * 0.8) * 0.02

            # スケール変化による位置補正（中心を維持）
            scaled_w = int(overlay_display_w * scale_factor)
            scaled_h = int(overlay_display_h * scale_factor)
            offset_x = (overlay_display_w - scaled_w) // 2
            offset_y = (overlay_display_h - scaled_h) // 2

            current_x = base_x + float_x + offset_x
            current_y = base_y + float_y + offset_y
            return (current_x, current_y)
        else:
            return (base_x, base_y)

    overlay_clip = overlay_clip.with_position(overlay_position)

    print(f"✓ オーバーレイクリップ作成完了（{animation}アニメーション）")

    # ==========================================
    # 4. 動画とオーバーレイを合成（letterbox付き）
    # ==========================================
    print("\n【4】動画を合成中（letterbox付き）...")

    def make_final_frame(t):
        """時間tに応じた最終フレームを生成（白い背景 + 縮小動画 + オーバーレイ）"""
        # 白い背景キャンバスを作成
        canvas = Image.new('RGB', (canvas_w, canvas_h), background_color)

        # 動画のフレームを取得して縮小
        video_frame = video_clip.get_frame(t)
        video_frame_img = Image.fromarray(video_frame)
        video_frame_scaled = video_frame_img.resize(
            (scaled_video_w, scaled_video_h),
            Image.Resampling.LANCZOS
        )

        # 縮小した動画を中央に配置
        canvas.paste(video_frame_scaled, (0, video_y_offset))

        # オーバーレイ画像を取得
        overlay_frame = make_overlay_frame(t)
        overlay_frame_img = Image.fromarray(overlay_frame)

        # オーバーレイ位置を計算
        if animation == "float":
            float_x = math.sin(t * 1.2) * 15 + math.sin(t * 0.7) * 8
            float_y = math.cos(t * 1.5) * 10 + math.cos(t * 0.9) * 5
            scale_factor = 1.0 + math.sin(t * 0.8) * 0.02

            # スケール変化による位置補正
            scaled_w = int(overlay_display_w * scale_factor)
            scaled_h = int(overlay_display_h * scale_factor)
            offset_x = (overlay_display_w - scaled_w) // 2
            offset_y = (overlay_display_h - scaled_h) // 2

            current_x = int(base_x + float_x + offset_x)
            current_y = int(base_y + float_y + offset_y)
        else:
            current_x = base_x
            current_y = base_y

        # オーバーレイを配置（RGBA対応）
        canvas.paste(overlay_frame_img, (current_x, current_y), overlay_frame_img)

        # 上部に白い帯を被せる
        if top_bar_height > 0:
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(canvas)
            draw.rectangle([(0, 0), (canvas_w, top_bar_height)], fill=background_color)

            # 字幕を描画
            if subtitle_text:
                try:
                    # フォント設定（ヒラギノフォント）
                    fontsize = 70
                    try:
                        font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", fontsize)
                    except:
                        try:
                            font = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", fontsize)
                        except:
                            font = ImageFont.load_default()

                    # テキストのサイズを取得
                    bbox = draw.textbbox((0, 0), subtitle_text, font=font)
                    text_w = bbox[2] - bbox[0]
                    text_h = bbox[3] - bbox[1]

                    # 中央に配置
                    text_x = (canvas_w - text_w) // 2
                    text_y = (top_bar_height - text_h) // 2

                    # 黒い縁取り
                    for offset_x in range(-4, 5):
                        for offset_y in range(-4, 5):
                            if offset_x != 0 or offset_y != 0:
                                draw.text((text_x + offset_x, text_y + offset_y), subtitle_text, font=font, fill=(0, 0, 0))

                    # 字幕本体（黒）
                    draw.text((text_x, text_y), subtitle_text, font=font, fill=(0, 0, 0))
                except Exception as e:
                    print(f"⚠️  字幕描画エラー: {e}")

        return np.array(canvas)

    # カスタムクリップを作成
    final_clip = VideoClip(make_final_frame, duration=video_duration).with_fps(video_fps)

    # 元動画の音声を追加
    if video_clip.audio:
        final_clip = final_clip.with_audio(video_clip.audio)
        print("✓ 音声を引き継ぎました")

    print(f"✓ 合成完了")

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
    print("✅ 動画オーバーレイ追加完了！")
    print("=" * 60)
    print(f"📂 出力先: {output_path}")
    print(f"⏱️  動画の長さ: {video_duration:.2f}秒")
    print(f"📐 元動画: {video_w}x{video_h}")
    print(f"📐 縮小後: {scaled_video_w}x{scaled_video_h} ({video_scale * 100:.1f}%)")
    print(f"📐 出力解像度: {canvas_w}x{canvas_h} (元動画と同じ)")
    print(f"🎬 フレームレート: {video_fps}fps")
    print(f"📸 オーバーレイ: {overlay_display_w}x{overlay_display_h} @ {position}")
    print(f"✨ アニメーション: {animation}")
    print(f"🎨 背景色: RGB{background_color}")
    print("=" * 60)

    return output_path


def main():
    """CLI実行用のメイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='動画にオーバーレイを追加')
    parser.add_argument('--video', '-v', type=str, required=True,
                       help='入力動画パス')
    parser.add_argument('--output', '-o', type=str, required=True,
                       help='出力動画パス')
    parser.add_argument('--overlay', '-i', type=str, required=True,
                       help='オーバーレイ画像パス')
    parser.add_argument('--position', '-p', type=str, default='bottom',
                       choices=['bottom', 'top', 'left', 'right', 'center'],
                       help='オーバーレイ位置')
    parser.add_argument('--scale', '-s', type=float, default=0.35,
                       help='オーバーレイサイズ（動画の高さに対する割合）')
    parser.add_argument('--animation', '-a', type=str, default='float',
                       choices=['float', 'static'],
                       help='アニメーション種類')

    args = parser.parse_args()

    add_floating_overlay(
        video_path=Path(args.video),
        output_path=Path(args.output),
        overlay_image_path=Path(args.overlay),
        position=args.position,
        overlay_scale=args.scale,
        animation=args.animation
    )


if __name__ == '__main__':
    main()
