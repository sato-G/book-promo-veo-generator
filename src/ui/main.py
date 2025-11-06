#!/usr/bin/env python3
"""
Streamlit UIモジュール

書籍プロモーション動画生成のWebインターフェース
"""

import streamlit as st
from pathlib import Path
from src.generators.veo3_sample import check_api_key, generate_video_from_upload


def main():
    """Streamlit UIのメイン関数"""

    st.title("📚 書籍プロモーション動画生成")

    # API Key確認
    api_key_ok, message = check_api_key()
    if api_key_ok:
        st.success("✅ API Key設定済み")
    else:
        st.error(f"❌ {message}")
        st.stop()

    # 画像アップロード
    uploaded_file = st.file_uploader("書籍表紙画像", type=["png", "jpg", "jpeg"])

    if uploaded_file:
        st.image(uploaded_file, width=300)
        st.success(f"画像がアップロードされました: {uploaded_file.name}")

    # プロンプト入力
    prompt = st.text_area("プロンプト", value="本のタイトルが浮かび上がる", height=100)

    # 動画の長さ
    duration = st.selectbox("動画の長さ（秒）", options=[4, 6, 8], index=2)

    # 動画生成ボタン
    if st.button("🎥 動画を生成", disabled=(uploaded_file is None or not prompt.strip())):
        try:
            # 動画生成
            with st.spinner("⏳ 動画を生成中... 数分かかります"):
                output_path = generate_video_from_upload(
                    uploaded_file=uploaded_file,
                    prompt=prompt,
                    duration=duration,
                    output_dir=Path("output"),
                )

                st.success(f"✅ 動画生成完了: {output_path}")

            # 生成された動画を表示
            if output_path.exists():
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


if __name__ == "__main__":
    main()
