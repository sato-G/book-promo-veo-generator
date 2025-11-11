#!/usr/bin/env python3
"""
冒頭アニメーション生成モジュール

書籍プロモーション動画の冒頭用の回転ズームバックアニメーション
360度回転しながらズームバックする迫力のある演出
"""

from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tempfile
from moviepy import ImageClip, CompositeVideoClip, VideoClip, AudioFileClip


def generate_opening_animation(
    image_path: Path,
    output_path: Path,
    catchphrase: Optional[str] = None,
    duration: float = 2.0,  # 合計2秒（0.2秒アニメ + 1.8秒停止）
    animation_duration: float = 0.2,  # アニメーション部分（0.2秒）
    zoom_start: float = 2.5,
    zoom_end: float = 1.0,
    resolution: Tuple[int, int] = (1080, 1920),
    fps: int = 30,
    enable_tts: bool = False  # TTSナレーションを有効化
) -> Path:
    """
    冒頭の回転ズームバックアニメーション動画を生成

    Args:
        image_path: 入力画像パス（書籍の表紙など）
        output_path: 出力動画パス
        catchphrase: キャッチコピー（字幕として画像中央に表示）
        duration: 動画の長さ（秒）デフォルト0.2秒
        zoom_start: 開始時の拡大率（デフォルト2.5倍）
        zoom_end: 終了時の拡大率（デフォルト1.0倍）
        resolution: 動画解像度 (width, height)
        fps: フレームレート

    Returns:
        出力動画のパス
    """
    print("=" * 60)
    print("🎬 冒頭アニメーション生成開始")
    print("=" * 60)
    print(f"📸 入力画像: {image_path}")
    print(f"⏱️  動画の長さ: {duration}秒")
    print(f"🔍 ズーム: {zoom_start}x → {zoom_end}x")
    if catchphrase:
        print(f"💬 キャッチコピー: {catchphrase}")
    print("=" * 60 + "\n")

    # 出力ディレクトリを作成
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # ==========================================
    # 1. 画像を読み込んでリサイズ
    # ==========================================
    print("【1】画像を読み込み中...")
    img = Image.open(image_path)

    # アスペクト比を保ちながらリサイズ
    img_w, img_h = img.size
    target_w, target_h = resolution

    # 画像が縦長（9:16）か横長（16:9）かを判定
    img_aspect = img_w / img_h
    target_aspect = target_w / target_h

    if img_aspect > target_aspect:
        # 画像が横長 → 高さ基準でリサイズ
        new_h = target_h
        new_w = int(img_w * (target_h / img_h))
    else:
        # 画像が縦長 → 幅基準でリサイズ
        new_w = target_w
        new_h = int(img_h * (target_w / img_w))

    img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    print(f"✓ 画像リサイズ完了: {img_w}x{img_h} → {new_w}x{new_h}")

    # ==========================================
    # 2. 字幕付き画像を作成
    # ==========================================
    print("\n【2】字幕付き画像を作成中...")

    # 元画像に字幕を焼き込む
    base_img_with_subtitle = img_resized.copy()

    if catchphrase:
        print(f"   字幕を画像に焼き込み中: {catchphrase}")
        # RGB画像に変換
        if base_img_with_subtitle.mode != 'RGB':
            base_img_with_subtitle = base_img_with_subtitle.convert('RGB')

        draw = ImageDraw.Draw(base_img_with_subtitle)

        # フォント設定（ヒラギノフォント - 大きく）
        fontsize = 100  # 60 → 100（より大きく）
        try:
            font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", fontsize)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", fontsize)
            except:
                font = ImageFont.load_default()

        # 2行に分割（10文字以上なら中央で改行）
        lines = []
        if len(catchphrase) >= 10:
            # 中央あたりで分割
            mid = len(catchphrase) // 2
            # 区切り文字で分割を試みる
            best_split = mid
            for i in range(mid - 3, mid + 4):
                if i > 0 and i < len(catchphrase):
                    if catchphrase[i] in ['、', '。', '！', '？', '?', ' ']:
                        best_split = i + 1
                        break
            lines = [catchphrase[:best_split].strip(), catchphrase[best_split:].strip()]
        else:
            lines = [catchphrase]

        # 各行のサイズを計算
        line_heights = []
        max_width = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            line_heights.append(line_height)
            max_width = max(max_width, line_width)

        # 行間
        line_spacing = 20
        total_height = sum(line_heights) + line_spacing * (len(lines) - 1)

        # 位置を計算（画面中央）
        start_y = (new_h - total_height) // 2

        # 各行を描画
        current_y = start_y
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (new_w - text_width) // 2

            # 黒い縁取り（さらに太く）
            for offset_x in range(-6, 7):
                for offset_y in range(-6, 7):
                    if offset_x != 0 or offset_y != 0:
                        draw.text((x + offset_x, current_y + offset_y), line, font=font, fill=(0, 0, 0))

            # テキストを描画（黄色 - ゴールド）
            draw.text((x, current_y), line, font=font, fill=(255, 215, 0))

            current_y += line_heights[i] + line_spacing

        print(f"   ✓ 字幕焼き込み完了（{len(lines)}行、黄色、フォントサイズ{fontsize}）")

    # 画像をnumpy配列に変換
    img_array = np.array(base_img_with_subtitle)

    # ==========================================
    # 3. ズームバックアニメーションクリップを作成
    # ==========================================
    print("\n【3】ズームバックアニメーションを作成中...")

    def make_frame(t):
        """時間tに応じたフレームを生成（回転しながらズームバック効果、その後停止）"""
        if t < animation_duration:
            # Phase 1: アニメーション (0 → animation_duration)
            progress = t / animation_duration
            # 現在のズーム率（拡大 → 元サイズ）
            current_zoom = zoom_start + (zoom_end - zoom_start) * progress
            # 回転角度（360度回転）
            rotation_angle = 360 * progress
        else:
            # Phase 2: 静止 (animation_duration → duration)
            # 最終フレームで停止（正面、拡大なし）
            current_zoom = zoom_end  # 1.0x
            rotation_angle = 0  # 正面（回転なし）

        # ズームを適用した画像サイズ
        zoomed_w = int(new_w * current_zoom)
        zoomed_h = int(new_h * current_zoom)

        # PIL Imageでリサイズ
        zoomed_img = Image.fromarray(img_array).resize(
            (zoomed_w, zoomed_h),
            Image.Resampling.LANCZOS
        )

        # 回転を適用（expand=Trueで回転後の画像全体を含む）
        rotated_img = zoomed_img.rotate(
            -rotation_angle,  # 時計回り
            resample=Image.Resampling.BICUBIC,
            expand=True,
            fillcolor=(0, 0, 0)
        )

        # 回転後のサイズ
        rot_w, rot_h = rotated_img.size

        # 中央クロップして目標サイズにする
        left = (rot_w - target_w) // 2
        top = (rot_h - target_h) // 2

        # クロップ範囲を計算
        crop_left = max(0, left)
        crop_top = max(0, top)
        crop_right = min(rot_w, left + target_w)
        crop_bottom = min(rot_h, top + target_h)

        cropped = rotated_img.crop((crop_left, crop_top, crop_right, crop_bottom))

        # 黒背景のキャンバスを作成
        canvas = Image.new('RGB', resolution, (0, 0, 0))

        # 中央に配置
        paste_x = (target_w - cropped.width) // 2
        paste_y = (target_h - cropped.height) // 2
        canvas.paste(cropped, (paste_x, paste_y))

        return np.array(canvas)

    # カスタムクリップを作成
    final_clip = VideoClip(make_frame, duration=duration).with_fps(fps)

    print(f"✓ 回転ズームアニメーション作成完了 ({zoom_start}x → {zoom_end}x, 360度回転)")

    # ==========================================
    # 4. ナレーション音声を生成（オプション）
    # ==========================================
    narration_audio = None
    if enable_tts and catchphrase:
        print("\n【4】ナレーション音声を生成中...")
        try:
            from src.generators.text_to_speech_client import TextToSpeechClient

            tts_client = TextToSpeechClient()
            result = tts_client.synthesize_speech(
                text=catchphrase,
                output_name="opening_narration",
                language_code="ja-JP",
                voice_name=tts_client.JAPANESE_VOICES["male_b"],  # より低い声
                voice_gender="MALE",
                speaking_rate=1.4,  # より早く
                pitch=-8.0,  # かなり低め
                volume_gain_db=3.0,
                output_dir=Path("data/output/speech")
            )

            if result['status'] == 'success':
                narration_audio = AudioFileClip(str(result['audio_file']))
                print(f"✓ ナレーション音声生成完了: {narration_audio.duration:.2f}秒")

                # 動画に音声を追加
                final_clip = final_clip.with_audio(narration_audio)
            else:
                print("⚠️  ナレーション音声生成失敗（音声なしで続行）")
        except Exception as e:
            print(f"⚠️  ナレーション音声生成スキップ: {e}")
            print("✓ 音声なしで続行します")

    # ==========================================
    # 5. 動画を出力
    # ==========================================
    print("\n【5】動画を出力中...")
    final_clip.write_videofile(
        str(output_path),
        fps=fps,
        codec='libx264',
        audio=(narration_audio is not None),  # 音声があれば含める
        preset='medium',
        threads=4
    )

    print("\n" + "=" * 60)
    print("✅ 冒頭アニメーション生成完了！")
    print("=" * 60)
    print(f"📂 出力先: {output_path}")
    print(f"⏱️  動画の長さ: {duration}秒")
    print(f"📐 解像度: {resolution[0]}x{resolution[1]}")
    print(f"🎬 フレームレート: {fps}fps")
    print(f"🎙️  ナレーション: {'あり' if narration_audio else 'なし'}")
    print("=" * 60)

    return output_path


def main():
    """CLI実行用のメイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='冒頭アニメーション動画生成')
    parser.add_argument('--image', '-i', type=str, required=True,
                       help='入力画像パス')
    parser.add_argument('--output', '-o', type=str, required=True,
                       help='出力動画パス')
    parser.add_argument('--catchphrase', '-c', type=str, default=None,
                       help='キャッチコピー（字幕）')
    parser.add_argument('--duration', '-d', type=float, default=3.0,
                       help='動画の長さ（秒）')
    parser.add_argument('--zoom-start', type=float, default=1.5,
                       help='開始時の拡大率')
    parser.add_argument('--zoom-end', type=float, default=1.0,
                       help='終了時の拡大率')

    args = parser.parse_args()

    generate_opening_animation(
        image_path=Path(args.image),
        output_path=Path(args.output),
        catchphrase=args.catchphrase,
        duration=args.duration,
        zoom_start=args.zoom_start,
        zoom_end=args.zoom_end
    )


if __name__ == '__main__':
    main()
