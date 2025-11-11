#!/usr/bin/env python3
"""
Streamlit UIモジュール

書籍プロモーション動画生成のWebインターフェース
"""

import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加（Streamlit実行場所に依存しないため）
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from src.generators.veo3_sample import check_api_key, generate_video_from_upload
from src.generators.veo3_talking_video import generate_video as generate_talking_video
from src.generators.explainer_slideshow import generate_explainer, build_narration_segments
from src.generators.cover_card_generator import generate_cover_card
from src.generators.nanobana_client import NanobanaClient
from src.generators.gemini_text_to_image import generate_images as gemini_generate_images
from src.generators.video_concat import concat_videos
import os
from PIL import Image, ImageDraw, ImageFont


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

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Veo3 画像→動画 (Simple)",
        "Veo3 Talking Video (口パク)",
        "Explainer Slideshow",
        "Cover Card",
        "Text to Image",
        "Concat Videos"
    ])

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

    # --- Tab 3: Explainer Slideshow ---
    with tab3:
        st.subheader("Explainer Slideshow（テキスト→字幕/TTS→スライド）")

        # 入力テキスト
        default_text = (
            "ストレスでお腹が痛い/胃が重い背景にはCRHが関与。受容体I/IIの発現により、\n"
            "胃の運動は抑制され、大腸の蠕動は促進されることがある。朝はCRHが高く、\n"
            "通勤時のストレスで症状が出やすい。詳しくは本書で。最後に書影をご覧ください。"
        )
        text_input = st.text_area(
            "説明テキスト（長文OK・自動分割）",
            value=default_text,
            height=220,
            help="句読点で自然に分割。画像枚数に合わせて自動調整します。"
        )

        # 画像アップロード or プレースホルダー生成
        st.markdown("---")
        st.caption("画像は未用意でもOK。プレースホルダーで試せます。")
        uploaded_imgs = st.file_uploader(
            "解説用画像（複数可）", type=["png","jpg","jpeg"], accept_multiple_files=True, key="expl_imgs"
        )
        cover_img = st.file_uploader("書影（オプション・最後に配置）", type=["png","jpg","jpeg"], key="expl_cover")

        num_slides = st.slider("スライド枚数（書影除く）", min_value=3, max_value=12, value=5, step=1)
        total_images_preview = (len(uploaded_imgs) if uploaded_imgs else num_slides) + (1 if cover_img else 0)
        st.caption(f"最終的な画像枚数プレビュー: {total_images_preview}枚（書影含む）")

        duration = st.slider("動画の長さ（秒）", 30, 180, 75, 5)
        enable_tts = st.checkbox("TTSで音声も生成（推奨）", value=True)

        final_title = st.text_input("最終スライドのタイトル（書影に重ねる字幕・任意）", value="")

        # 画像プロンプトの提案（nanobana向け）
        if st.button("🧠 画像プロンプト案を表示"):
            segs = [s["text"] for s in build_narration_segments(text_input or default_text, num_slides + (1 if cover_img else 0), duration)]
            st.markdown("**セグメント別のイメージ指示（例）**")
            for i, s in enumerate(segs, 1):
                hint = "表紙（書影）" if (cover_img and i == len(segs)) else "内容イメージ"
                st.text(f"[{i}] {hint}: {s[:80]}…")
            st.info("この案を基に nanobana で画像を生成し、上でアップロードしてください。")

        # 生成
        if st.button("🎬 Explainer 動画を生成", disabled=not (text_input.strip())):
            try:
                # 画像を一時保存 or プレースホルダー生成
                temp_dir = Path("temp/explainer")
                temp_dir.mkdir(parents=True, exist_ok=True)

                image_paths = []
                if uploaded_imgs and len(uploaded_imgs) > 0:
                    for uf in uploaded_imgs:
                        p = temp_dir / uf.name
                        with open(p, "wb") as f:
                            f.write(uf.getbuffer())
                        image_paths.append(p)
                    # 足りなければプレースホルダーで補完
                    while len(image_paths) < num_slides:
                        idx = len(image_paths) + 1
                        ph = temp_dir / f"placeholder_{idx}.png"
                        _make_placeholder(ph, idx)
                        image_paths.append(ph)
                    # 多ければ指定数に丸め
                    image_paths = image_paths[:num_slides]
                else:
                    # すべてプレースホルダー
                    for idx in range(1, num_slides + 1):
                        ph = temp_dir / f"placeholder_{idx}.png"
                        _make_placeholder(ph, idx)
                        image_paths.append(ph)

                cover_path = None
                if cover_img:
                    cover_path = temp_dir / ("cover_" + cover_img.name)
                    with open(cover_path, "wb") as f:
                        f.write(cover_img.getbuffer())

                with st.spinner("⏳ 生成中... TTS有効時は音声長に同期します"):
                    out = generate_explainer(
                        text=text_input or default_text,
                        images=image_paths,
                        add_cover=cover_path,
                        duration=duration,
                        enable_tts=enable_tts,
                        final_title=final_title.strip() or None,
                        output_dir=Path("data/output"),
                    )

                st.success(f"✅ 動画生成完了: {out}")
                if Path(out).exists():
                    st.video(str(out))
                    with open(out, "rb") as vf:
                        st.download_button(
                            label="📥 動画をダウンロード",
                            data=vf,
                            file_name=Path(out).name,
                            mime="video/mp4",
                            key="dl_expl",
                        )
            except Exception as e:
                st.error(f"❌ エラー: {e}")
                st.exception(e)

    # --- Tab 4: Cover Card ---
    with tab4:
        st.subheader("Cover Card（表紙＋タイトルの締めカット）")

        cover_file = st.file_uploader("表紙画像をアップロード (PNG/JPG)", type=["png", "jpg", "jpeg"], key="cover_upl")
        title_text = st.text_input("タイトル（字幕）", value="")
        subtitle_text = st.text_input("サブタイトル（既定: 続きは本書で）", value="続きは本書で")
        colA, colB, colC = st.columns(3)
        with colA:
            duration = st.slider("長さ(秒)", min_value=2, max_value=6, value=3, step=1)
        with colB:
            y_offset = st.slider("字幕の位置(上→下)", min_value=120, max_value=600, value=360, step=10)
        with colC:
            font_size = st.slider("文字サイズ", min_value=72, max_value=140, value=110, step=2)

        colD, colE = st.columns(2)
        with colD:
            use_tts = st.checkbox("TTSナレーションを付ける", value=True)
        with colE:
            tts_speed = st.slider("話速", min_value=1.0, max_value=2.0, value=1.6, step=0.1)

        if st.button("🎬 Cover Card を生成", disabled=(cover_file is None)):
            try:
                temp_dir = Path("temp/cover")
                temp_dir.mkdir(parents=True, exist_ok=True)
                cover_path = temp_dir / cover_file.name
                with open(cover_path, "wb") as f:
                    f.write(cover_file.getbuffer())

                narration_text = f"{title_text}。{subtitle_text}。" if use_tts else None

                with st.spinner("⏳ 生成中..."):
                    out = generate_cover_card(
                        cover_image=cover_path,
                        title=title_text.strip() or None,
                        subtitle=subtitle_text.strip() or None,
                        duration=duration,
                        subtitle_position="top",
                        subtitle_fontsize=font_size,
                        subtitle_color=(255, 230, 0),
                        subtitle_y=y_offset,
                        narration_text=narration_text,
                        tts_speed=tts_speed,
                        output_path=None,
                    )

                st.success(f"✅ 動画生成完了: {out}")
                if Path(out).exists():
                    st.video(str(out))
                    with open(out, "rb") as vf:
                        st.download_button(
                            label="📥 動画をダウンロード",
                            data=vf,
                            file_name=Path(out).name,
                            mime="video/mp4",
                            key="dl_cover",
                        )
            except Exception as e:
                st.error(f"❌ エラー: {e}")
                st.exception(e)

    # --- Tab 5: Text to Image backends ---
    with tab5:
        st.subheader("Text to Image（nanobana / Gemini）")

        sub_tab1, sub_tab2 = st.tabs(["nanobana CLI", "Gemini API"])

        # nanobana CLI backend
        with sub_tab1:
            nanobana_cmd = os.getenv("NANOBANA_CMD")
            if nanobana_cmd:
                st.success("✅ NANOBANA_CMD 設定済み: 実画像を生成します")
                with st.expander("現在のコマンドテンプレート", expanded=False):
                    st.code(nanobana_cmd)
            else:
                st.warning("⚠️ NANOBANA_CMD 未設定: プレースホルダー画像で動作確認します")

            default_prompts = "\n".join([
                "朝のジョギング、自然光、爽やか、写真風、縦長1080x1920、余白多め、被写体は匿名",
                "室内ストレッチ、やわらかい日差し、写真風、落ち着いた配色、清潔感",
                "ウォーキング、緑道、早朝、写真風、ミニマル構図",
                "軽い筋トレ（自重）、自宅のリビング、写真風、整った背景、雑多な物は映らない",
            ])

            prompts_text = st.text_area(
                "プロンプト（1行=1画像）",
                value=default_prompts,
                height=160,
                help="各行が1枚の生成対象になります。テイスト統一なら前置きを揃えてください。",
                key="nanobana_prompts",
            )

            out_base = Path("data/generated/nanobana")
            import time as _t
            subdir = out_base / str(int(_t.time()))

            if st.button("🖼️ 画像を生成 (nanobana)"):
                try:
                    prompt_list = [ln.strip() for ln in (prompts_text or "").splitlines() if ln.strip()]
                    if not prompt_list:
                        st.error("プロンプトを1行以上入力してください")
                    else:
                        client = NanobanaClient()
                        with st.spinner("⏳ 生成中..."):
                            paths = client.generate_images(prompt_list, out_dir=subdir)
                        st.success(f"✅ 生成完了: {len(paths)}枚 → {subdir}")

                        cols = st.columns(2)
                        for i, p in enumerate(paths):
                            with cols[i % 2]:
                                st.image(str(p), caption=p.name, use_container_width=True)
                        st.info("Explainerタブでアップロードすると、そのまま動画化できます")
                except Exception as e:
                    st.error(f"❌ 生成エラー: {e}")
                    st.exception(e)

        # Gemini API backend
        with sub_tab2:
            st.caption("Gemini 2.5 Flash Image を使用（GOOGLE_API_KEYが必要）")
            g_prompt = st.text_area(
                "プロンプト",
                value="A realistic photo of a Shiba Inu sitting on a wooden floor, vertical 1080x1920, natural light, clean background",
                height=100,
                key="gemini_prompt",
            )
            g_n = st.slider("生成枚数", min_value=1, max_value=4, value=1, step=1, key="gemini_n")
            g_model = st.text_input("モデル", value="gemini-2.5-flash-image", key="gemini_model")

            out_dir = Path("data/generated/gemini")
            if st.button("🖼️ 画像を生成 (Gemini)"):
                try:
                    with st.spinner("⏳ 生成中..."):
                        paths = gemini_generate_images(
                            prompt=g_prompt.strip(),
                            n=g_n,
                            model=g_model.strip() or "gemini-2.5-flash-image",
                            output_dir=out_dir,
                        )
                    if paths:
                        st.success(f"✅ 生成完了: {len(paths)}枚 → {out_dir}")
                        cols = st.columns(2)
                        for i, p in enumerate(paths):
                            with cols[i % 2]:
                                st.image(str(p), caption=p.name, use_container_width=True)
                        st.info("Explainerタブでアップロードすると、そのまま動画化できます")
                    else:
                        st.warning("画像パートが返りませんでした。権限・クォータ・モデル指定をご確認ください。")
                except Exception as e:
                    st.error(f"❌ 生成エラー: {e}")
                    st.exception(e)

    # --- Tab 6: Concat Videos ---
    with tab6:
        st.subheader("Concat Videos（複数動画を順番に連結）")

        uploaded_videos = st.file_uploader(
            "動画を選択（複数）", type=["mp4", "mov", "m4v"], accept_multiple_files=True
        )

        # 並び順管理
        order_key = "concat_order"
        if uploaded_videos:
            if order_key not in st.session_state or len(st.session_state[order_key]) != len(uploaded_videos):
                st.session_state[order_key] = list(range(len(uploaded_videos)))

            st.caption("アップロード順で初期化。上下ボタンで並び替え可能です。")
            ordered = [uploaded_videos[i] for i in st.session_state[order_key]]
            for idx, uf in enumerate(ordered):
                c1, c2, c3 = st.columns([6, 1, 1])
                with c1:
                    st.text(f"{idx+1}. {uf.name}")
                with c2:
                    if st.button("↑", key=f"concat_up_{idx}", disabled=(idx == 0)):
                        o = st.session_state[order_key]
                        o[idx], o[idx-1] = o[idx-1], o[idx]
                        st.rerun()
                with c3:
                    if st.button("↓", key=f"concat_dn_{idx}", disabled=(idx == len(ordered)-1)):
                        o = st.session_state[order_key]
                        o[idx], o[idx+1] = o[idx+1], o[idx]
                        st.rerun()

        st.markdown("---")
        cA, cB, cC = st.columns(3)
        with cA:
            fps = st.number_input("出力FPS", min_value=1, max_value=120, value=24)
        with cB:
            res_text = st.text_input("解像度 (例: 1080x1920)", value="1080x1920")
        with cC:
            method = st.selectbox("連結方法", options=["compose", "chain"], index=0)

        def _parse_res(txt: str):
            try:
                w, h = txt.lower().split("x")
                return int(w), int(h)
            except Exception:
                return None

        if st.button("🎬 連結して書き出す", disabled=not uploaded_videos):
            try:
                temp_dir = Path("temp/concat")
                temp_dir.mkdir(parents=True, exist_ok=True)
                paths = []
                for i in st.session_state.get(order_key, []):
                    uf = uploaded_videos[i]
                    p = temp_dir / uf.name
                    with open(p, "wb") as f:
                        f.write(uf.getbuffer())
                    paths.append(p)

                out_dir = Path("data/output")
                out_dir.mkdir(parents=True, exist_ok=True)
                import time as _t
                out = out_dir / f"merged_{int(_t.time())}.mp4"

                res = _parse_res(res_text.strip()) if res_text.strip() else None
                with st.spinner("⏳ 連結中..."):
                    merged = concat_videos(
                        inputs=paths,
                        output=out,
                        fps=int(fps) if fps else None,
                        resolution=res,
                        method=method,
                    )

                st.success(f"✅ 連結完了: {merged}")
                if merged.exists():
                    st.video(str(merged))
                    with open(merged, "rb") as vf:
                        st.download_button(
                            label="📥 動画をダウンロード",
                            data=vf,
                            file_name=merged.name,
                            mime="video/mp4",
                            key="dl_concat",
                        )
            except Exception as e:
                st.error(f"❌ エラー: {e}")
                st.exception(e)


def _make_placeholder(path: Path, idx: int, size=(1080, 1920)):
    """簡易プレースホルダー画像を作成"""
    img = Image.new("RGB", size, (30, 30, 40))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc", 140)
    except:
        font = ImageFont.load_default()
    text = f"Slide {idx}"
    tw, th = draw.textbbox((0, 0), text, font=font)[2:4]
    x = (size[0] - tw) // 2
    y = (size[1] - th) // 2
    # 影
    draw.text((x+4, y+4), text, font=font, fill=(0,0,0))
    draw.text((x, y), text, font=font, fill=(230, 230, 240))
    img.save(path)


if __name__ == "__main__":
    main()
