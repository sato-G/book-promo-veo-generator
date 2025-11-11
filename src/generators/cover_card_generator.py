#!/usr/bin/env python3
"""
Cover Card Generator

書影（表紙）を中央に配置した短いエンディング用動画を生成。

特徴
- 入力画像を中央トリミング（2:3近辺）→ 縦型キャンバス(1080x1920)に配置
- 背景は表紙画像のブラー拡大で雰囲気統一
- 最終字幕としてタイトルや「続きは本書で」を重ね表示（任意）
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple
import tempfile

from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageFont
from moviepy import ImageClip, CompositeVideoClip, AudioFileClip

# サブモジュールとしても、スクリプトとしても動くようにインポートを調整
try:
    from .text_to_speech_client import TextToSpeechClient  # パッケージ実行時
except Exception:
    try:
        import sys
        from pathlib import Path as _Path
        _PROJECT_ROOT = _Path(__file__).resolve().parents[2]
        if str(_PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(_PROJECT_ROOT))
        from src.generators.text_to_speech_client import TextToSpeechClient  # 直叩き実行時
    except Exception:
        TextToSpeechClient = None  # TTSなしで継続


def _center_crop_to_aspect(img: Image.Image, target_aspect: float = 2/3) -> Image.Image:
    w, h = img.size
    current = w / h
    if abs(current - target_aspect) < 0.02:
        return img
    if current > target_aspect:
        # too wide → crop width
        new_w = int(h * target_aspect)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    else:
        # too tall → crop height
        new_h = int(w / target_aspect)
        top = (h - new_h) // 2
        return img.crop((0, top, w, top + new_h))


def _prepare_background(src: Image.Image, size: Tuple[int, int]) -> Path:
    bg = ImageOps.fit(src, size, method=Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(30))
    # 暗めにして前景を目立たせる
    overlay = Image.new("RGB", size, (0, 0, 0))
    bg = Image.blend(bg, overlay, 0.2)
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    bg.save(tf.name, "JPEG", quality=95)
    tf.close()
    return Path(tf.name)


def _prepare_cover_resized(src: Image.Image, max_w: int, max_h: int) -> Path:
    img = src.copy()
    img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    # 白縁/影を付ける
    padding = 16
    shadow = 24
    w, h = img.size
    canvas = Image.new("RGBA", (w + padding*2 + shadow, h + padding*2 + shadow), (0, 0, 0, 0))
    # 影
    shadow_img = Image.new("RGBA", (w + padding*2, h + padding*2), (0, 0, 0, 160))
    shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(18))
    canvas.paste(shadow_img, (shadow, shadow), shadow_img)
    # 白フチ
    frame = Image.new("RGBA", (w + padding*2, h + padding*2), (255, 255, 255, 255))
    canvas.paste(frame, (0, 0), frame)
    # 画像本体
    canvas.paste(img.convert("RGBA"), (padding, padding), img.convert("RGBA"))
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    canvas.save(tf.name)
    tf.close()
    return Path(tf.name)


def _subtitle_overlay(
    text: str,
    size: Tuple[int, int],
    *,
    position: str = "top",  # "top" or "bottom"
    color: Tuple[int, int, int] = (255, 230, 0),  # yellow-ish
    fontsize: int = 88,
    y_offset: int = 120,
) -> Path:
    W, H = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # フォント
    try:
        font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", fontsize)
    except Exception:
        font = ImageFont.load_default()

    # 改行を尊重しつつ、各行を幅で折り返し
    max_w = int(W * 0.9)
    lines = []
    base_lines = (text or "").split("\n")
    for base in base_lines:
        buf = ""
        for ch in base:
            t = buf + ch
            box = draw.textbbox((0, 0), t, font=font)
            if box[2] - box[0] > max_w and buf:
                lines.append(buf)
                buf = ch
            else:
                buf = t
        if buf:
            lines.append(buf)

    # 位置（下部）
    total_h = 0
    line_boxes = []
    for line in lines:
        box = draw.textbbox((0, 0), line, font=font)
        line_boxes.append(box)
        total_h += (box[3] - box[1]) + 8

    if position == "top":
        y = max(40, y_offset)
    else:
        y = max(40, H - y_offset - total_h)
    for i, line in enumerate(lines):
        box = line_boxes[i]
        lw = box[2] - box[0]
        x = (W - lw) // 2
        # 縁取り
        for dx in range(-4, 5):
            for dy in range(-4, 5):
                if dx or dy:
                    draw.text((x+dx, y+dy), line, font=font, fill=(0, 0, 0, 255))
        draw.text((x, y), line, font=font, fill=(color[0], color[1], color[2], 255))
        y += (box[3] - box[1]) + 8

    tf = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    img.save(tf.name)
    tf.close()
    return Path(tf.name)


def generate_cover_card(
    *,
    cover_image: Path,
    output_path: Optional[Path] = None,
    resolution: Tuple[int, int] = (1080, 1920),
    duration: float = 6.0,
    title: Optional[str] = None,
    subtitle: Optional[str] = "続きは本書で",
    subtitle_position: str = "top",
    subtitle_fontsize: int = 88,
    subtitle_color: Tuple[int, int, int] = (255, 230, 0),
    subtitle_y: int = 120,
    narration_text: Optional[str] = None,
    tts_speed: float = 1.3,
) -> Path:
    W, H = resolution
    src = Image.open(cover_image)
    # 中央トリミング(2:3近傍)
    cropped = _center_crop_to_aspect(src, 2/3)

    bg_path = _prepare_background(cropped, (W, H))
    cover_path = _prepare_cover_resized(cropped, int(W*0.62), int(H*0.8))

    bg_clip = ImageClip(str(bg_path)).with_duration(duration)
    cover_clip = ImageClip(str(cover_path)).with_duration(duration).with_position(("center", "center"))

    overlays = [bg_clip, cover_clip]

    # 字幕
    lines = []
    if title:
        lines.append(f"『{title}』")
    if subtitle:
        lines.append(subtitle)
    if lines:
        overlay_path = _subtitle_overlay(
            "\n".join(lines), (W, H), position=subtitle_position, color=subtitle_color, fontsize=subtitle_fontsize, y_offset=subtitle_y
        )
        overlays.append(ImageClip(str(overlay_path)).with_duration(duration))

    final = CompositeVideoClip(overlays, size=resolution)

    # オーディオ（任意のナレーション）
    audio_clip = None
    if narration_text or lines:
        try:
            if TextToSpeechClient is None:
                raise RuntimeError("TTS client unavailable")
            tts = TextToSpeechClient()
            speak_text = narration_text or "、".join(lines)
            result = tts.synthesize_speech(
                text=speak_text,
                output_name="cover_card",
                language_code="ja-JP",
                voice_name=tts.JAPANESE_VOICES.get("female_a"),
                voice_gender="FEMALE",
                speaking_rate=tts_speed,
                pitch=-2.0,
                volume_gain_db=2.0,
                output_dir=Path("data/output/speech"),
            )
            if result.get("status") == "success":
                audio_path = result["audio_file"]
                ac = AudioFileClip(str(audio_path))
                # 必要ならトリム/ループせず、短い場合は無音で終わる
                if ac.duration > duration:
                    ac = ac.subclipped(0, duration)
                final = final.with_audio(ac)
        except Exception as e:
            print(f"[cover_card] TTS failed or skipped: {e}")

    # 出力
    if output_path is None:
        import time
        ts = int(time.time())
        output_path = Path("data/output") / f"cover_card_{ts}.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.write_videofile(
        str(output_path), fps=24, codec="libx264", audio_codec="aac", preset="medium", bitrate="5000k"
    )
    return output_path


def main():
    import argparse
    p = argparse.ArgumentParser(description="Cover Card Generator")
    p.add_argument("--cover", type=Path, required=True, help="表紙画像のパス (PNG/JPG)")
    p.add_argument("--title", type=str, help="タイトル（字幕に表示）")
    p.add_argument("--subtitle", type=str, default="続きは本書で", help="サブタイトル")
    p.add_argument("--duration", type=float, default=6.0, help="動画の長さ（秒）")
    p.add_argument("--output", type=Path, help="出力パス（省略時はdata/output配下に自動命名）")
    p.add_argument("--pos", type=str, default="top", choices=["top","bottom"], help="字幕の位置")
    p.add_argument("--font-size", type=int, default=88, help="字幕フォントサイズ")
    p.add_argument("--narration", type=str, help="ナレーションテキスト（未指定時はタイトル+サブタイトルを読み上げ）")
    p.add_argument("--y", type=int, default=120, help="字幕の上下オフセット(px)。--pos topなら上から、bottomなら下からの距離")
    p.add_argument("--tts-speed", type=float, default=1.3, help="TTSの話速（1.0=通常、数値が大きいほど早口）")
    args = p.parse_args()

    out = generate_cover_card(
        cover_image=args.cover,
        title=args.title,
        subtitle=args.subtitle,
        duration=args.duration,
        output_path=args.output,
        subtitle_position=args.pos,
        subtitle_fontsize=args.font_size,
        subtitle_color=(255,230,0),
        narration_text=args.narration,
        subtitle_y=args.y,
        tts_speed=args.tts_speed,
    )
    print(f"✅ 出力: {out}")


if __name__ == "__main__":
    main()
