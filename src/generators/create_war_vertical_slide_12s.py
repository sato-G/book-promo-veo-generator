#!/usr/bin/env python3
"""
「あの戦争は何だったのか」縦型動画（横スライド切り替え）
- 12秒の動画
- 縦型（1080x1920）
- 横スライドで画像切り替え（4枚）
- ナレーション同期字幕
"""
from pathlib import Path
from moviepy import (
    ImageClip,
    CompositeVideoClip,
    AudioFileClip
)
from PIL import Image, ImageDraw, ImageFont
import tempfile
import numpy as np

# Text-to-Speechクライアントをインポート
from text_to_speech_client import TextToSpeechClient


def create_slide_transition_clip(
    image_path: Path,
    duration: float,
    resolution: tuple = (1080, 1920),
    slide_direction: str = 'left'  # 'left' or 'right'
):
    """
    横スライドトランジション + 横パン効果付きの画像クリップを作成

    Args:
        image_path: 画像パス
        duration: 表示時間
        resolution: 縦型解像度 (width, height) = (1080, 1920)
        slide_direction: スライド方向 ('left' = 左から右へ, 'right' = 右から左へ)

    Returns:
        スライド効果 + パン効果付きImageClip
    """
    target_width, target_height = resolution

    # パン効果用に少し広めの画像を作成（1.15倍の幅）
    pan_width = int(target_width * 1.15)
    max_pan_offset = pan_width - target_width

    # 画像を読み込んでリサイズ
    with Image.open(image_path) as img:
        # RGB変換
        if img.mode != 'RGB':
            img = img.convert('RGB')

        img_width, img_height = img.size
        img_aspect = img_width / img_height

        # 縦型にフィット（高さ基準）
        new_height = target_height
        new_width = int(new_height * img_aspect)

        # パン用の広めの幅を確保
        if new_width < pan_width:
            new_width = pan_width
            new_height = int(new_width / img_aspect)

        # リサイズ
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # 中央でクロップ（広めに）
        left = (new_width - pan_width) // 2
        top = (new_height - target_height) // 2
        cropped_img = resized_img.crop((left, top, left + pan_width, top + target_height))

        # 一時ファイルに保存
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        cropped_img.save(temp_file.name, 'JPEG', quality=95)
        temp_file.close()

    # トランジション時間（0.3秒）
    transition_duration = 0.3

    def slide_and_pan_effect(get_frame, t):
        """スライドイン + パン効果"""
        frame = get_frame(t)

        if t < transition_duration:
            # スライドイン中
            progress = t / transition_duration
            if slide_direction == 'left':
                # 左から右へスライドイン
                x_offset = int(target_width * (1 - progress))
                result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
                # 広い画像の左端から切り出し
                result[:, x_offset:] = frame[:, :target_width-x_offset]
                return result
            else:
                # 右から左へスライドイン
                x_offset = int(target_width * (1 - progress))
                result = np.zeros((target_height, target_width, 3), dtype=np.uint8)
                # 広い画像の右端から切り出し
                result[:, :target_width-x_offset] = frame[:, max_pan_offset+x_offset:max_pan_offset+target_width]
                return result
        else:
            # パン効果（トランジション後）
            pan_progress = (t - transition_duration) / (duration - transition_duration)

            if slide_direction == 'left':
                # 左から右へゆっくりパン
                pan_offset = int(max_pan_offset * pan_progress)
                return frame[:, pan_offset:pan_offset+target_width]
            else:
                # 右から左へゆっくりパン
                pan_offset = int(max_pan_offset * (1 - pan_progress))
                return frame[:, pan_offset:pan_offset+target_width]

    # 基本クリップを作成
    clip = ImageClip(temp_file.name).with_duration(duration)

    # スライド + パン効果を適用
    clip = clip.transform(slide_and_pan_effect)

    return clip


def create_subtitle_clip_vertical(
    text: str,
    start_time: float,
    duration: float,
    fontsize: int = 48,
    size: tuple = (1080, 1920)
):
    """
    縦型動画用の字幕クリップを作成

    Args:
        text: 字幕テキスト
        start_time: 開始時刻
        duration: 表示時間
        fontsize: フォントサイズ
        size: 画像サイズ

    Returns:
        ImageClip
    """
    # 透明背景の画像を作成
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # フォント設定
    try:
        font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", fontsize)
    except:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", fontsize)
        except:
            font = ImageFont.load_default()

    # テキストの境界ボックスを取得
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 位置を計算（下部中央）
    x = (size[0] - text_width) // 2
    y = size[1] - 250 - text_height

    # 黒い縁取り（太め）
    for offset_x in range(-4, 5):
        for offset_y in range(-4, 5):
            if offset_x != 0 or offset_y != 0:
                draw.text((x + offset_x, y + offset_y), text, font=font, fill=(0, 0, 0, 255))

    # テキストを描画（白）
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    # 一時ファイルに保存
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name)
    temp_file.close()

    # ImageClipとして返す
    return (ImageClip(temp_file.name, transparent=True)
            .with_duration(duration)
            .with_start(start_time))


def create_war_vertical_slide_12s(
    image_dir: str,
    output_path: str,
    narration_segments: list = None,
    bgm_path: str = None,
    duration: float = 12.0,
    resolution: tuple = (1080, 1920)
):
    """
    縦型動画を生成（横スライド切り替え）

    Args:
        image_dir: 画像ディレクトリ
        output_path: 出力パス
        narration_segments: ナレーションセグメント
        bgm_path: BGMファイルパス
        duration: 動画の長さ
        resolution: 解像度（縦型: 1080x1920）
    """
    image_dir = Path(image_dir)

    print("=" * 60)
    print("🎬 「あの戦争は何だったのか」縦型動画生成（横スライド）")
    print("=" * 60)

    # ==========================================
    # 1. 画像を選択（4枚）
    # ==========================================
    print("\n【1】画像を準備中...")

    # 画像ファイルを取得
    image_files = []
    for i in range(1, 11):
        compressed_path = image_dir / f"AI用素材_{i}_compressed.jpg"
        img_path = image_dir / f"AI用素材_{i}.jpg"

        if compressed_path.exists():
            image_files.append(compressed_path)
        elif img_path.exists():
            image_files.append(img_path)

    if not image_files:
        raise ValueError(f"画像が見つかりません: {image_dir}")

    # 最初の4枚を選択
    selected_images = image_files[:4]

    print(f"✓ 使用する画像: {len(selected_images)}枚")

    # ==========================================
    # 2. ナレーション音声を生成（セグメントごと）またはナレーションなしで字幕のみ
    # ==========================================
    updated_narration_segments = []
    actual_duration = duration  # デフォルトは指定された長さ

    if narration_segments:
        print("\n【2】字幕セグメントを準備中...")

        # まず字幕用のセグメントを準備（音声なし）
        current_time = 0.0
        segment_duration = duration / len(narration_segments)

        for i, segment in enumerate(narration_segments):
            updated_segment = {
                'text': segment['text'],
                'start': current_time,
                'duration': segment_duration
            }
            updated_narration_segments.append(updated_segment)
            print(f"   セグメント{i+1}: {segment_duration:.2f}秒 - {segment['text']}")
            current_time += segment_duration

        narration_segments = updated_narration_segments
        print(f"✓ 字幕セグメント準備完了: {len(narration_segments)}個")

        # 音声合成を試みる（失敗しても字幕は表示される）
        try:
            print("\n【2-オプション】ナレーション音声を生成中...")
            tts_client = TextToSpeechClient()

            audio_segments = []
            for i, segment in enumerate(narration_segments):
                result = tts_client.synthesize_speech(
                    text=segment['text'],
                    output_name=f"war_narration_segment_{i+1}",
                    language_code="ja-JP",
                    voice_name=tts_client.JAPANESE_VOICES["male_a"],
                    voice_gender="MALE",
                    speaking_rate=1.2,
                    pitch=-5.0,
                    volume_gain_db=3.0,
                    output_dir=Path("data/output/speech")
                )

                if result['status'] == 'success':
                    audio_clip = AudioFileClip(str(result['audio_file']))
                    audio_segments.append(audio_clip)
                    print(f"   ✓ セグメント{i+1}音声生成完了")

            if audio_segments and len(audio_segments) == len(narration_segments):
                from moviepy import concatenate_audioclips
                narration_audio = concatenate_audioclips(audio_segments)
                print(f"✓ ナレーション音声生成完了: {narration_audio.duration:.2f}秒")
            else:
                narration_audio = None
                print("⚠️  一部の音声生成に失敗しました（字幕のみ表示されます）")

        except Exception as e:
            print(f"⚠️  ナレーション音声生成スキップ: {e}")
            print("✓ 字幕のみで続行します")
            narration_audio = None
    else:
        narration_audio = None
        narration_segments = []

    # ==========================================
    # 3. パン＆クロップクリップを作成（ナレーション区切りに合わせて）
    # ==========================================
    print(f"\n【3】パン＆クロップクリップを作成中（動画の長さ: {actual_duration:.1f}秒）...")

    # ナレーションセグメントと画像の対応関係を計算
    # 画像枚数とセグメント数から自動的に割り当て
    num_images = len(selected_images)
    num_segments = len(narration_segments) if narration_segments else 1

    # 各画像にセグメントを均等に割り当て
    segments_per_image = num_segments / num_images

    image_timings = []

    for i in range(num_images):
        # この画像が担当するセグメントの範囲を計算
        start_segment = int(i * segments_per_image)
        end_segment = int((i + 1) * segments_per_image)

        if i == num_images - 1:
            # 最後の画像は残りのセグメント全てを担当
            end_segment = num_segments

        # 開始時刻と長さを計算
        if narration_segments:
            start_time = narration_segments[start_segment]['start']
            end_time = narration_segments[end_segment - 1]['start'] + narration_segments[end_segment - 1]['duration']
            duration = end_time - start_time
        else:
            start_time = i * (actual_duration / num_images)
            duration = actual_duration / num_images

        # 2枚目以降の画像は0.2秒早く開始（ナレーションより先に切り替え）
        transition_advance = 0.2
        if i > 0:
            start_time = max(0, start_time - transition_advance)
            duration += transition_advance

        image_timings.append({
            'image_path': selected_images[i],
            'start_time': start_time,
            'duration': duration,
            'segments': list(range(start_segment, end_segment))
        })

        print(f"   画像{i+1}: セグメント{start_segment+1}-{end_segment} ({duration:.2f}秒)")

    # クリップを作成
    video_clips = []

    for i, timing in enumerate(image_timings):
        # 交互にスライド方向を変える
        slide_direction = 'left' if i % 2 == 0 else 'right'

        clip = create_slide_transition_clip(
            timing['image_path'],
            timing['duration'],
            resolution=resolution,
            slide_direction=slide_direction
        )

        # 開始時刻を設定
        clip = clip.with_start(timing['start_time'])
        video_clips.append(clip)

        print(f"   {i+1}/{num_images}: {timing['image_path'].name} ({timing['start_time']:.2f}秒から{timing['duration']:.2f}秒間、slide from {slide_direction})")

    # CompositeVideoClipで合成
    main_video = CompositeVideoClip(video_clips, size=resolution)
    main_video = main_video.with_duration(actual_duration)

    print(f"✓ メイン動画作成完了（{main_video.duration:.1f}秒）")

    # ==========================================
    # 4. ナレーション同期字幕を追加
    # ==========================================
    print("\n【4】ナレーション同期字幕を追加中...")

    overlays = []

    if narration_segments:
        for segment in narration_segments:
            subtitle = create_subtitle_clip_vertical(
                text=segment['text'],
                start_time=segment['start'],
                duration=segment['duration'],
                fontsize=45,
                size=resolution
            )
            overlays.append(subtitle)

        print(f"✓ 字幕追加完了: {len(overlays)}個")
    else:
        print("⚠️  ナレーションセグメント未指定")

    # ==========================================
    # 5. BGMを追加
    # ==========================================
    bgm_audio = None

    if bgm_path and Path(bgm_path).exists():
        print("\n【5】BGMを追加中...")

        try:
            bgm_audio = AudioFileClip(bgm_path)

            if bgm_audio.duration > actual_duration:
                bgm_audio = bgm_audio.subclipped(0, actual_duration)

            # BGM音量を調整（15%に下げる）
            bgm_audio = bgm_audio.with_volume_scaled(0.15)

            print(f"✓ BGM追加完了: {bgm_path}")

        except Exception as e:
            print(f"⚠️  BGM追加失敗: {e}")
            bgm_audio = None
    else:
        print("\n【5】BGMをスキップ")

    # ==========================================
    # 6. 最終合成
    # ==========================================
    print("\n【6】最終合成中...")

    # ビデオクリップを合成
    video_clips_final = [main_video] + overlays
    final_video = CompositeVideoClip(video_clips_final, size=resolution)
    final_video = final_video.with_duration(actual_duration)

    # オーディオを合成
    audio_clips = []
    if narration_audio:
        audio_clips.append(narration_audio)
    if bgm_audio:
        audio_clips.append(bgm_audio)

    if audio_clips:
        from moviepy import CompositeAudioClip
        final_audio = CompositeAudioClip(audio_clips)
        final_video = final_video.with_audio(final_audio)

    # ==========================================
    # 7. 出力
    # ==========================================
    print("\n【7】動画を出力中...")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    final_video.write_videofile(
        str(output_path),
        fps=24,
        codec='libx264',
        audio_codec='aac' if audio_clips else None,
        preset='medium',
        bitrate='5000k'
    )

    print("\n" + "=" * 60)
    print("✅ 完成！")
    print("=" * 60)
    print(f"📁 出力ファイル: {output_path}")
    print(f"⏱️  動画の長さ: {actual_duration:.2f}秒")
    print(f"📐 解像度: {resolution[0]}x{resolution[1]} (縦型 9:16)")
    print(f"🎬 画像枚数: {len(selected_images)}枚")
    print(f"📝 字幕: {len(overlays)}個 (ナレーション同期)")
    print(f"🎙️  ナレーション: {'あり' if narration_audio else 'なし'}")
    print(f"🎵 BGM: {'あり' if bgm_audio else 'なし'}")
    print(f"✨ アニメーション: パン＆クロップ（ゆっくり）")
    print("=" * 60)


def main():
    """メイン関数"""

    # 設定
    image_dir = "data/『あの戦争は何だったのか』/images"
    output_path = "data/output/ano_senso_vertical_slide_12s.mp4"

    # ナレーションセグメント（音声の長さに合わせて自動調整）
    narration_segments = [
        {
            "text": "日本はどこで間違えたのか?",
            "start": 0.0,
            "duration": 3.0
        },
        {
            "text": "掲げた理想はすべて誤りだったのか?",
            "start": 3.0,
            "duration": 3.0
        },
        {
            "text": "「大東亜」は日本をどう見ていたか?",
            "start": 6.0,
            "duration": 3.0
        },
        {
            "text": "戦後80年、今こそ問い直す",
            "start": 9.0,
            "duration": 2.0
        },
        {
            "text": "「私たちにとっての戦争」とは。",
            "start": 11.0,
            "duration": 2.0
        }
    ]

    # BGMパス
    bgm_path = "data/bgm/yoiyaminoseaside.mp3"

    # 動画生成
    create_war_vertical_slide_12s(
        image_dir=image_dir,
        output_path=output_path,
        narration_segments=narration_segments,
        bgm_path=bgm_path,
        duration=12.0,
        resolution=(1080, 1920)  # 縦型 9:16
    )


if __name__ == "__main__":
    main()
