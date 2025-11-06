#!/usr/bin/env python3
"""
書籍プロモーション動画エディター
- 既存動画に本の表紙・タイトルをオーバーレイ
- インタラクティブに配置やスタイルを調整
"""
import streamlit as st
from pathlib import Path
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, TextClip
from PIL import Image, ImageDraw, ImageFont
import tempfile

# ページ設定
st.set_page_config(
    page_title="書籍プロモーション動画エディター",
    page_icon="📚",
    layout="wide"
)

st.title("📚 書籍プロモーション動画エディター")
st.markdown("動画に本の表紙やタイトルをオーバーレイして、プロモーション動画を作成します")

# サイドバー：設定
st.sidebar.header("⚙️ 設定")

# 動画選択
video_dir = Path("data/output")
video_files = sorted(video_dir.glob("*.mp4"))
video_names = [v.name for v in video_files]

selected_video = st.sidebar.selectbox(
    "📹 動画を選択",
    video_names,
    index=video_names.index("war_marching_final.mp4") if "war_marching_final.mp4" in video_names else 0
)

# 本のデータを取得
book_dirs = {
    "あの戦争は何だったのか": "data/『あの戦争は何だったのか』",
    "腸と脳の科学": "data/『「腸と脳」の科学』",
    "土と生命の46億年史": "data/『土と生命の46億年史』"
}

selected_book = st.sidebar.selectbox(
    "📖 書籍を選択",
    list(book_dirs.keys())
)

# レイアウト設定
st.sidebar.subheader("📐 レイアウト")

layout_mode = st.sidebar.radio(
    "レイアウトモード",
    ["タイトル上部固定", "表紙右側固定", "表紙＋タイトル"]
)

# タイトル設定
if layout_mode in ["タイトル上部固定", "表紙＋タイトル"]:
    st.sidebar.subheader("📝 タイトル設定")

    title_text = st.sidebar.text_input(
        "タイトルテキスト",
        value=selected_book
    )

    title_fontsize = st.sidebar.slider(
        "フォントサイズ",
        20, 80, 40
    )

    title_position = st.sidebar.selectbox(
        "位置",
        ["上部中央", "上部左", "上部右"]
    )

    title_bg_opacity = st.sidebar.slider(
        "背景の不透明度",
        0.0, 1.0, 0.7
    )

# 表紙設定
if layout_mode in ["表紙右側固定", "表紙＋タイトル"]:
    st.sidebar.subheader("🖼️ 表紙設定")

    cover_size = st.sidebar.slider(
        "サイズ（%）",
        10, 50, 25
    )

    cover_position = st.sidebar.selectbox(
        "位置",
        ["右上", "右下", "左上", "左下"]
    )

    cover_margin = st.sidebar.slider(
        "余白（px）",
        10, 100, 30
    )

# プレビュー生成ボタン
if st.sidebar.button("🎬 プレビュー生成", type="primary"):
    with st.spinner("動画を生成中..."):
        try:
            # 元動画を読み込み
            video_path = video_dir / selected_video
            video = VideoFileClip(str(video_path))

            clips = [video]

            # タイトルオーバーレイ
            if layout_mode in ["タイトル上部固定", "表紙＋タイトル"]:
                # タイトル画像を作成
                width = int(video.w)
                height = int(title_fontsize * 2)

                title_img = Image.new('RGBA', (width, height), (0, 0, 0, int(255 * title_bg_opacity)))
                draw = ImageDraw.Draw(title_img)

                try:
                    font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", title_fontsize)
                except:
                    font = ImageFont.load_default()

                bbox = draw.textbbox((0, 0), title_text, font=font)
                text_width = bbox[2] - bbox[0]

                # 位置決定
                if title_position == "上部中央":
                    text_x = (width - text_width) // 2
                elif title_position == "上部左":
                    text_x = 30
                else:  # 上部右
                    text_x = width - text_width - 30

                text_y = (height - title_fontsize) // 2

                draw.text((text_x, text_y), title_text, font=font, fill=(255, 255, 255, 255))

                # 一時ファイルに保存
                temp_title = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                title_img.save(temp_title.name)
                temp_title.close()

                title_clip = ImageClip(temp_title.name, transparent=True).with_duration(video.duration)
                title_clip = title_clip.with_position(("center", 0))
                clips.append(title_clip)

            # 表紙オーバーレイ
            if layout_mode in ["表紙右側固定", "表紙＋タイトル"]:
                # 表紙画像を探す
                book_dir = Path(book_dirs[selected_book])
                cover_files = list(book_dir.glob("表紙.*")) + list(book_dir.glob("*カバー*.png")) + list(book_dir.glob("*カバー*.pdf"))

                if cover_files:
                    cover_path = cover_files[0]

                    # PDFの場合は画像に変換済みのものを使用
                    if cover_path.suffix == '.pdf':
                        cover_img_files = list(book_dir.glob("表紙.png")) + list(book_dir.glob("表紙.jpg"))
                        if cover_img_files:
                            cover_path = cover_img_files[0]

                    if cover_path.suffix in ['.png', '.jpg', '.jpeg']:
                        cover_img = Image.open(cover_path)

                        # RGBAの場合はRGBに変換
                        if cover_img.mode == 'RGBA':
                            background = Image.new('RGB', cover_img.size, (255, 255, 255))
                            background.paste(cover_img, mask=cover_img.split()[3])
                            cover_img = background
                        elif cover_img.mode != 'RGB':
                            cover_img = cover_img.convert('RGB')

                        # サイズ調整
                        target_width = int(video.w * cover_size / 100)
                        aspect = cover_img.height / cover_img.width
                        target_height = int(target_width * aspect)

                        cover_img = cover_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

                        # 一時ファイルに保存
                        temp_cover = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
                        cover_img.save(temp_cover.name, 'JPEG', quality=95)
                        temp_cover.close()

                        # 位置決定
                        if cover_position == "右上":
                            pos = (video.w - target_width - cover_margin, cover_margin)
                        elif cover_position == "右下":
                            pos = (video.w - target_width - cover_margin, video.h - target_height - cover_margin)
                        elif cover_position == "左上":
                            pos = (cover_margin, cover_margin)
                        else:  # 左下
                            pos = (cover_margin, video.h - target_height - cover_margin)

                        cover_clip = ImageClip(temp_cover.name).with_duration(video.duration)
                        cover_clip = cover_clip.with_position(pos)
                        clips.append(cover_clip)

            # 合成
            final = CompositeVideoClip(clips)

            # 一時ファイルに出力
            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            final.write_videofile(
                temp_output.name,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                preset='fast',
                logger=None
            )

            # セッション状態に保存
            st.session_state.preview_video = temp_output.name
            st.success("✅ プレビュー生成完了！")

        except Exception as e:
            st.error(f"❌ エラーが発生しました: {str(e)}")

# メインエリア：プレビュー表示
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎥 プレビュー")

    if 'preview_video' in st.session_state:
        st.video(st.session_state.preview_video)

        # ダウンロードボタン
        with open(st.session_state.preview_video, 'rb') as f:
            st.download_button(
                label="📥 動画をダウンロード",
                data=f,
                file_name=f"{selected_book}_promo.mp4",
                mime="video/mp4"
            )
    else:
        st.info("左側の設定を調整して「プレビュー生成」ボタンを押してください")

with col2:
    st.subheader("📋 現在の設定")
    st.write(f"**動画:** {selected_video}")
    st.write(f"**書籍:** {selected_book}")
    st.write(f"**レイアウト:** {layout_mode}")

    if layout_mode in ["タイトル上部固定", "表紙＋タイトル"]:
        st.write(f"**タイトル:** {title_text}")
        st.write(f"**位置:** {title_position}")

    if layout_mode in ["表紙右側固定", "表紙＋タイトル"]:
        st.write(f"**表紙サイズ:** {cover_size}%")
        st.write(f"**表紙位置:** {cover_position}")

# フッター
st.markdown("---")
st.markdown("💡 **ヒント:** 設定を変更したら「プレビュー生成」ボタンを押して確認できます")
