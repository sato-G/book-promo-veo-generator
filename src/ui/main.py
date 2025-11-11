#!/usr/bin/env python3
"""
Streamlit UIモジュール

書籍プロモーション動画生成のWebインターフェース
"""

import streamlit as st
from pathlib import Path
from src.generators.veo3_sample import check_api_key, generate_video_from_upload
from src.generators.veo3_talking_video import generate_video as generate_talking_video


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

    tab1, tab2 = st.tabs(["Veo3 画像→動画 (Simple)", "Veo3 Talking Video (口パク)"])

    # --- Tab 1: 既存のシンプル生成（表紙の動きなど） ---
    with tab1:
        st.subheader("Veo3 画像→動画 (Simple)")

        uploaded_file = st.file_uploader(
            "画像をアップロード", type=["png", "jpg", "jpeg"], key="uploader_simple"
        )
        if uploaded_file:
            st.image(uploaded_file, width=300)
            st.success(f"画像がアップロードされました: {uploaded_file.name}")

        prompt = st.text_area(
            "プロンプト",
            value="本のタイトルが浮かび上がる",
            height=100,
            key="prompt_simple",
        )

        if st.button("🎥 動画を生成", disabled=(uploaded_file is None or not prompt.strip()), key="btn_simple"):
            try:
                with st.spinner("⏳ 動画を生成中... 数分かかります"):
                    output_path = generate_video_from_upload(
                        uploaded_file=uploaded_file,
                        prompt=prompt,
                        output_dir=Path("data/output"),
                    )

                    st.success(f"✅ 動画生成完了: {output_path}")

                if output_path.exists():
                    st.video(str(output_path))
                    with open(output_path, "rb") as video_file:
                        st.download_button(
                            label="📥 動画をダウンロード",
                            data=video_file,
                            file_name=output_path.name,
                            mime="video/mp4",
                            key="dl_simple",
                        )
            except Exception as e:
                st.error(f"❌ エラー: {e}")
                st.exception(e)

    # --- Tab 2: Talking Video（口パク重視） ---
    with tab2:
        st.subheader("Veo3 Talking Video（口パク重視）")

        uploaded_talk = st.file_uploader(
            "人物画像をアップロード", type=["png", "jpg", "jpeg"], key="uploader_talk"
        )
        if uploaded_talk:
            st.image(uploaded_talk, width=300)
            st.success(f"画像がアップロードされました: {uploaded_talk.name}")

        default_talk_prompt = (
            "ショット: 正面のバストショット。カメラは固定し、揺れや過度なズームは避ける。\n"
            "被写体: 入力画像の人物。顔の造形・髪型・衣服の一貫性を保つ。自然な瞬きと微細な表情。\n"
            "口の動き: セリフと正確に同期。過度な頭の揺れを避ける。\n"
            "会話: 「記憶力の低下、不眠、うつ、発達障害、肥満、高血圧、糖尿病、感染症の重症化……すべての不調は腸から始まる!」\n"
            "発話かな: 「きおくりょくのていか、ふみん、うつ、はったつしょうがい、ひまん、こうけつあつ、とうにょうびょう、かんせんしょうのじゅうしょうか……すべてのふちょうはちょうからはじまる！」\n"
            "表示: 字幕は表示しない。フリッカーや歪みを避け、実写的でクリアな質感。約6秒。"
        )

        talk_prompt = st.text_area(
            "プロンプト（テンプレは自由編集可・字幕は出しません）",
            value=default_talk_prompt,
            height=220,
            key="prompt_talk",
        )

        if st.button(
            "🎙️ Talking Video を生成",
            disabled=(uploaded_talk is None or not talk_prompt.strip()),
            key="btn_talk",
        ):
            try:
                # 一時ファイルに保存してからジェネレータへ渡す
                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)
                temp_image = temp_dir / uploaded_talk.name
                with open(temp_image, "wb") as f:
                    f.write(uploaded_talk.getbuffer())

                with st.spinner("⏳ Talking Video を生成中... 数分かかります"):
                    out = generate_talking_video(
                        image_path=temp_image,
                        prompt=talk_prompt,
                        output_dir=Path("data/output"),
                        model="veo-3.0-generate-001",
                        debug=False,
                    )

                st.success(f"✅ 動画生成完了: {out}")
                if Path(out).exists():
                    st.video(str(out))
                    with open(out, "rb") as video_file:
                        st.download_button(
                            label="📥 動画をダウンロード",
                            data=video_file,
                            file_name=Path(out).name,
                            mime="video/mp4",
                            key="dl_talk",
                        )
            except Exception as e:
                st.error(f"❌ エラー: {e}")
                st.exception(e)


if __name__ == "__main__":
    main()
