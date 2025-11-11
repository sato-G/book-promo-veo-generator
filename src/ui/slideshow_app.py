#!/usr/bin/env python3
"""
スライドショー動画生成 Streamlit UI

画像からスライドショー動画を生成するWebインターフェース
"""

import streamlit as st
from pathlib import Path
import sys
import tempfile
from typing import List
import re

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.generators.slideshow_generator import generate_slideshow


def save_uploaded_file(uploaded_file, output_dir: Path) -> Path:
    """アップロードされたファイルを保存"""
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def get_bgm_library() -> dict:
    """BGMライブラリを取得"""
    bgm_dir = project_root / "BGM"
    bgm_files = {}

    if bgm_dir.exists():
        for file in bgm_dir.glob("*.mp3"):
            # ファイル名から日本語表示名を生成
            name = file.stem
            display_names = {
                "yoiyaminoseaside": "宵闇のシーサイド",
                "natsuyasuminotanken": "夏休みの探検",
                "neonpurple": "ネオンパープル",
                "yume": "夢"
            }
            display_name = display_names.get(name, name)
            bgm_files[display_name] = str(file)

    return bgm_files


def split_text_by_images(text: str, num_images: int) -> List[str]:
    """
    テキストを画像枚数に必ず合わせて分割（自然な区切り優先）

    1. まず句点（。！？?）で1文ずつに分割
    2. 足りなければ読点（、）で追加分割
    3. 多ければ自然に結合して、必ず画像枚数と同じ数にする

    Args:
        text: 分割するテキスト
        num_images: 画像枚数（この数に必ず合わせる）

    Returns:
        必ずnum_images個の要素を持つリスト
    """
    text_clean = text.replace('\n', '')

    # 1文ずつに分割（句点で区切る - 全角・半角両方対応）
    sentences = re.split(r'([。！？\?])', text_clean)

    # 句点を前の文に結合
    segments = []
    i = 0
    while i < len(sentences):
        if i + 1 < len(sentences) and sentences[i+1] in '。！？?':
            # 句点があれば結合
            segments.append(sentences[i] + sentences[i+1])
            i += 2
        elif sentences[i].strip():
            # 句点がなくても内容があれば追加
            segments.append(sentences[i])
            i += 1
        else:
            i += 1

    segments = [s.strip() for s in segments if s.strip()]

    # 足りなければ読点でも分割
    if len(segments) < num_images:
        new_segments = []
        for seg in segments:
            parts = re.split(r'(、)', seg)
            temp = []
            i = 0
            while i < len(parts):
                if i + 1 < len(parts) and parts[i+1] == '、':
                    temp.append(parts[i] + parts[i+1])
                    i += 2
                elif parts[i].strip():
                    temp.append(parts[i])
                    i += 1
                else:
                    i += 1
            new_segments.extend([s.strip() for s in temp if s.strip()])
        if new_segments:
            segments = new_segments

    # セグメントがまだ足りない、または多すぎる場合は調整
    if len(segments) != num_images and segments:
        if len(segments) < num_images:
            # 足りない場合：最も長いものを分割
            while len(segments) < num_images:
                max_idx = max(range(len(segments)), key=lambda i: len(segments[i]))
                longest = segments[max_idx]
                if len(longest) > 1:
                    mid = len(longest) // 2
                    segments[max_idx] = longest[:mid]
                    segments.insert(max_idx + 1, longest[mid:])
                else:
                    # 分割できない場合は空文字を追加
                    segments.append("")
        else:
            # 多い場合：均等に結合
            step = len(segments) / num_images
            new_segments = []
            for i in range(num_images):
                start = int(i * step)
                end = int((i + 1) * step)
                combined = ''.join(segments[start:end])
                new_segments.append(combined)
            segments = new_segments

    # 最終結果：必ず num_images 個
    result = []
    for i in range(num_images):
        if i < len(segments) and segments[i].strip():
            result.append(segments[i].strip())
        else:
            result.append("...")

    return result


def main():
    """Streamlit UIのメイン関数"""

    st.set_page_config(
        page_title="スライドショー動画生成",
        page_icon="🎬",
        layout="wide"
    )

    st.title("🎬 スライドショー動画生成")
    st.markdown("複数の画像からスライドショー動画を生成します")

    # サイドバー：設定
    with st.sidebar:
        st.header("⚙️ 基本設定")

        # 動画の長さ
        duration = st.slider(
            "動画の長さ (秒)",
            min_value=6,
            max_value=60,
            value=12,
            step=1
        )

        # 解像度
        resolution_options = {
            "縦型 (1080x1920)": (1080, 1920),
            "横型 (1920x1080)": (1920, 1080),
            "正方形 (1080x1080)": (1080, 1080),
        }
        resolution_label = st.selectbox(
            "解像度",
            options=list(resolution_options.keys()),
            index=0
        )
        resolution = resolution_options[resolution_label]

        st.markdown("---")
        st.header("🎨 アニメーション")

        # スライド方向
        slide_pattern = st.selectbox(
            "スライド方向",
            options=["左右交互", "左のみ", "右のみ"],
            index=0,
            help="画像のスライドイン方向"
        )

        # 切り替えタイミング
        transition_advance = st.slider(
            "切り替えタイミング (秒早く)",
            min_value=0.0,
            max_value=0.5,
            value=0.2,
            step=0.05,
            help="画像切り替えをナレーションより何秒早く開始するか"
        )

        # パン効果
        pan_enabled = st.checkbox("横パン効果", value=True, help="画像を横にゆっくり移動")
        pan_scale = st.slider(
            "パン幅",
            min_value=1.0,
            max_value=1.3,
            value=1.15,
            step=0.05,
            disabled=not pan_enabled,
            help="画像を何倍の幅で読み込むか"
        ) if pan_enabled else 1.0

    # メインエリア
    st.header("📸 画像アップロード")
    uploaded_images = st.file_uploader(
        "画像を選択（複数可）",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=True,
        help="スライドショーに使用する画像を選択してください"
    )

    # 画像の順番を管理するためのsession_state
    if uploaded_images:
        # 新しい画像がアップロードされた場合のみ初期化
        if 'image_order' not in st.session_state or len(st.session_state.image_order) != len(uploaded_images):
            st.session_state.image_order = list(range(len(uploaded_images)))

        st.success(f"✅ {len(uploaded_images)}枚の画像がアップロードされました")

    # ナレーションと BGM を横並び
    col1, col2 = st.columns(2)

    # ナレーション分割用の変数（後で画像と一緒に表示するため）
    narration_segments_preview = None

    with col1:
        st.header("🎤 ナレーション")
        enable_narration = st.checkbox("ナレーションを追加", value=True)

        narration_text = ""
        if enable_narration:
            narration_text = st.text_area(
                "ナレーションテキスト",
                height=150,
                max_chars=200,
                placeholder="ナレーションを入力してください（70文字程度推奨）\n画像枚数に応じて自動的に分割されます。",
                help="入力したテキストは画像枚数に応じて自動分割されます"
            )

            if narration_text and uploaded_images:
                char_count = len(narration_text)
                st.caption(f"文字数: {char_count}文字")

                # ナレーションを分割
                narration_segments_preview = split_text_by_images(narration_text, len(uploaded_images))

    with col2:
        st.header("🎵 BGM")

        # BGMライブラリを取得
        bgm_library = get_bgm_library()

        if bgm_library:
            bgm_option = st.selectbox(
                "BGMを選択",
                options=["なし"] + list(bgm_library.keys()),
                index=0,
                help="ライブラリからBGMを選択してください"
            )

            selected_bgm_path = bgm_library.get(bgm_option) if bgm_option != "なし" else None

            if selected_bgm_path:
                st.success(f"✅ 選択中: {bgm_option}")
        else:
            st.warning("⚠️ BGMライブラリが見つかりません")
            selected_bgm_path = None

    # 画像とナレーションの対応表示
    if uploaded_images and narration_segments_preview:
        st.markdown("---")
        st.subheader(f"📝 画像とナレーションの対応（全{len(uploaded_images)}枚）")

        # 順番に並べ替えた画像リスト
        ordered_images = [uploaded_images[i] for i in st.session_state.image_order]

        # コンテナで明示的に全て表示
        with st.container():
            # 縦一列で表示
            for img_idx in range(len(ordered_images)):
                img = ordered_images[img_idx]
                narration = narration_segments_preview[img_idx]

                cols = st.columns([1, 4, 1, 1])

                with cols[0]:
                    st.image(img, width=120)

                with cols[1]:
                    st.text(f"{img_idx+1}. {narration}")

                with cols[2]:
                    if st.button("↑", key=f"up2_{img_idx}", disabled=(img_idx == 0)):
                        order = st.session_state.image_order
                        order[img_idx], order[img_idx-1] = order[img_idx-1], order[img_idx]
                        st.rerun()

                with cols[3]:
                    if st.button("↓", key=f"down2_{img_idx}", disabled=(img_idx == len(ordered_images)-1)):
                        order = st.session_state.image_order
                        order[img_idx], order[img_idx+1] = order[img_idx+1], order[img_idx]
                        st.rerun()

    # 動画生成ボタン
    st.markdown("---")

    can_generate = (
        uploaded_images is not None and
        len(uploaded_images) >= 2 and
        (not enable_narration or narration_text.strip())
    )

    if st.button(
        "🎬 動画を生成",
        disabled=not can_generate,
        type="primary",
        use_container_width=True
    ):
        try:
            # 順番に並べ替えた画像リストを使用
            ordered_images = [uploaded_images[i] for i in st.session_state.image_order]

            # 一時ディレクトリに画像を保存
            temp_dir = Path(tempfile.mkdtemp())
            image_paths = []

            with st.spinner("📤 画像を準備中..."):
                for uploaded_img in ordered_images:
                    img_path = save_uploaded_file(uploaded_img, temp_dir)
                    image_paths.append(img_path)

            # 出力パス
            import time
            timestamp = int(time.time())
            output_path = Path("data/output") / f"slideshow_{timestamp}.mp4"

            # ナレーションセグメントの準備
            final_narration_segments = None
            if enable_narration and narration_text.strip():
                # テキストを画像枚数で分割
                segments = split_text_by_images(narration_text, len(image_paths))

                # 各セグメントに均等な時間を割り当て
                segment_duration = duration / len(segments)
                final_narration_segments = []
                for i, seg_text in enumerate(segments):
                    final_narration_segments.append({
                        "text": seg_text,
                        "start": i * segment_duration,
                        "duration": segment_duration
                    })

            # BGMパス
            bgm_path = Path(selected_bgm_path) if selected_bgm_path else None

            # 動画生成
            with st.spinner("🎬 動画を生成中... しばらくお待ちください"):
                output_path = generate_slideshow(
                    image_paths=image_paths,
                    output_path=output_path,
                    narration_segments=final_narration_segments,
                    bgm_path=bgm_path,
                    duration=duration,
                    resolution=resolution,
                    transition_advance=transition_advance,
                    pan_enabled=pan_enabled,
                    pan_scale=pan_scale,
                    enable_tts=enable_narration
                )

            st.success(f"✅ 動画生成完了！")

            # 生成された動画を表示（小さめ）
            if output_path.exists():
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    st.video(str(output_path))

                # ダウンロードボタン
                with open(output_path, "rb") as video_file:
                    st.download_button(
                        label="📥 動画をダウンロード",
                        data=video_file,
                        file_name=output_path.name,
                        mime="video/mp4",
                    )

        except Exception as e:
            st.error(f"❌ エラー: {e}")
            st.exception(e)

    # 使い方の説明
    with st.expander("📖 使い方"):
        st.markdown("""
        ### スライドショー動画の作り方

        1. **画像を選択**: 2枚以上の画像をアップロード
        2. **ナレーション入力**: テキストを一括入力（自動的に画像枚数で分割されます）
        3. **BGM選択**: ライブラリからBGMを選択（オプション）
        4. **設定調整**: サイドバーでアニメーション効果を調整
        5. **動画生成**: 「動画を生成」ボタンをクリック

        ### アニメーション効果

        - **スライド方向**: 画像のスライドイン方向（左右交互/左のみ/右のみ）
        - **横パン**: 表示中の画像がゆっくり横に移動
        - **切り替えタイミング**: ナレーションより少し早く画像を切り替え

        ### Tips

        - ナレーションは70文字程度が最適です
        - 画像は選択した順番で表示されます
        - BGMの音量は自動的に15%に調整されます
        - テキストは句読点で自動分割されます
        """)


if __name__ == "__main__":
    main()
