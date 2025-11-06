#!/usr/bin/env python3
"""
MoviePy動画効果
ズーム、パン、オーバーレイなど
"""
from pathlib import Path
from moviepy import ImageClip, VideoFileClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import tempfile
import numpy as np


def create_zoom_effect(
    image_path: Path,
    duration: float = 8.0,
    resolution: tuple = (1280, 720),
    zoom_factor: float = 1.3
) -> ImageClip:
    """
    画像にズームイン効果を追加

    Args:
        image_path: 入力画像パス
        duration: 動画の長さ（秒）
        resolution: 出力解像度
        zoom_factor: ズーム倍率

    Returns:
        ズーム効果付きのImageClip
    """
    img = Image.open(image_path)

    # RGBAの場合はRGBに変換
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    img_width, img_height = img.size

    # アスペクト比を保持してリサイズ
    target_width, target_height = resolution
    target_aspect = target_width / target_height
    img_aspect = img_width / img_height

    if img_aspect > target_aspect:
        new_height = target_height
        new_width = int(new_height * img_aspect)
    else:
        new_width = target_width
        new_height = int(new_width / img_aspect)

    # ズーム用に大きめにリサイズ
    scaled_width = int(new_width * zoom_factor)
    scaled_height = int(new_height * zoom_factor)

    resized_img = img.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)

    # 一時ファイルに保存
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    resized_img.save(temp_file.name, 'JPEG', quality=95)
    temp_file.close()

    def zoom_effect(get_frame, t):
        """ズームイン効果"""
        frame = get_frame(t)
        h, w = frame.shape[:2]

        progress = t / duration

        zoom_range_w = w - target_width
        zoom_range_h = h - target_height

        x_offset = int(zoom_range_w * (1 - progress) / 2)
        y_offset = int(zoom_range_h * (1 - progress) / 2)

        cropped = frame[y_offset:y_offset + target_height, x_offset:x_offset + target_width]

        return cropped

    clip = ImageClip(temp_file.name).with_duration(duration)
    clip = clip.transform(zoom_effect)

    return clip


def create_pan_zoom_effect(
    image_path: Path,
    duration: float = 8.0,
    resolution: tuple = (1280, 720)
) -> ImageClip:
    """
    画像にパン&ズーム効果を追加

    Args:
        image_path: 入力画像パス
        duration: 動画の長さ（秒）
        resolution: 出力解像度

    Returns:
        パン&ズーム効果付きのImageClip
    """
    img = Image.open(image_path)

    if img.mode != 'RGB':
        img = img.convert('RGB')

    target_width, target_height = resolution
    scale_factor = 1.5

    new_width = int(target_width * scale_factor)
    new_height = int(target_height * scale_factor)

    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    resized_img.save(temp_file.name, 'JPEG', quality=95)
    temp_file.close()

    def dynamic_effect(get_frame, t):
        """パンとズームを組み合わせた効果"""
        frame = get_frame(t)
        h, w = frame.shape[:2]

        progress = t / duration

        zoom_range_w = w - target_width
        zoom_range_h = h - target_height

        if progress < 0.3:
            # 開始: 左寄りから
            x_offset = 0
            y_offset = int(zoom_range_h * 0.5)
        elif progress < 0.7:
            # 中盤: 左から右へパン
            pan_progress = (progress - 0.3) / 0.4
            x_offset = int(zoom_range_w * pan_progress * 0.8)
            y_offset = int(zoom_range_h * (0.5 + pan_progress * 0.2))
        else:
            # 終盤: 中央にフォーカス
            final_progress = (progress - 0.7) / 0.3
            x_offset = int(zoom_range_w * (0.8 + final_progress * 0.1))
            y_offset = int(zoom_range_h * (0.7 - final_progress * 0.2))

        cropped = frame[y_offset:y_offset + target_height, x_offset:x_offset + target_width]

        return cropped

    clip = ImageClip(temp_file.name).with_duration(duration)
    clip = clip.transform(dynamic_effect)

    return clip


def create_text_overlay(
    text: str,
    duration: float,
    size: tuple,
    fontsize: int = 70,
    position: str = "center"
) -> ImageClip:
    """
    テキストオーバーレイを作成

    Args:
        text: テキスト
        duration: 表示時間
        size: 画像サイズ
        fontsize: フォントサイズ
        position: 位置 ("center", "top", "bottom")

    Returns:
        テキストオーバーレイのImageClip
    """
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", fontsize)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 位置決定
    x = (size[0] - text_width) // 2

    if position == "top":
        y = 50
    elif position == "bottom":
        y = size[1] - text_height - 50
    else:  # center
        y = (size[1] - text_height) // 2

    # 黒い縁取り
    for offset_x in range(-5, 6):
        for offset_y in range(-5, 6):
            if offset_x != 0 or offset_y != 0:
                draw.text((x + offset_x, y + offset_y), text, font=font, fill=(0, 0, 0, 255))

    # テキストを描画（白）
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name)
    temp_file.close()

    return ImageClip(temp_file.name, transparent=True).with_duration(duration)


def add_book_overlay(
    video: VideoFileClip,
    book_cover_path: Path = None,
    book_title: str = None,
    layout: str = "title_top"
) -> CompositeVideoClip:
    """
    動画に本の表紙やタイトルをオーバーレイ

    Args:
        video: 元動画
        book_cover_path: 本の表紙画像パス
        book_title: 本のタイトル
        layout: レイアウト ("title_top", "cover_right", "both")

    Returns:
        オーバーレイ付きの動画
    """
    clips = [video]

    if layout in ["title_top", "both"] and book_title:
        # タイトルオーバーレイ
        title = create_text_overlay(
            text=book_title,
            duration=video.duration,
            size=(int(video.w), int(video.h)),
            fontsize=40,
            position="top"
        )
        clips.append(title)

    if layout in ["cover_right", "both"] and book_cover_path and book_cover_path.exists():
        # 表紙オーバーレイ
        cover_img = Image.open(book_cover_path)

        if cover_img.mode == 'RGBA':
            background = Image.new('RGB', cover_img.size, (255, 255, 255))
            background.paste(cover_img, mask=cover_img.split()[3])
            cover_img = background
        elif cover_img.mode != 'RGB':
            cover_img = cover_img.convert('RGB')

        # サイズ調整（動画の25%）
        target_width = int(video.w * 0.25)
        aspect = cover_img.height / cover_img.width
        target_height = int(target_width * aspect)

        cover_img = cover_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

        temp_cover = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        cover_img.save(temp_cover.name, 'JPEG', quality=95)
        temp_cover.close()

        # 右上に配置
        pos = (video.w - target_width - 30, 30)
        cover_clip = ImageClip(temp_cover.name).with_duration(video.duration)
        cover_clip = cover_clip.with_position(pos)
        clips.append(cover_clip)

    return CompositeVideoClip(clips)
