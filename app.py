#!/usr/bin/env python3
"""
書籍プロモーション動画生成 - Streamlit UI

Veo 3.1を使って書籍表紙画像から動画を生成するWebアプリケーション。
"""

import os
import sys
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# 両方の動画生成モジュールをインポート
sys.path.insert(0, str(Path(__file__).parent))
from generators.veo3_sample import generate_video as generate_video_simple
from generators.veo3_talking_video import generate_video as generate_video_talking


def main():
    """Streamlit メインアプリケーション"""

    st.set_page_config(
        page_title="書籍プロモーション動画生成",
        page_icon="📚",
        layout="wide"
    )

    st.title("📚 書籍プロモーション動画生成")
    st.markdown("Google Veo 3を使って、書籍表紙や人物画像からプロモーション動画を生成します。")

    # サイドバー: 設定
    with st.sidebar:
        st.header("⚙️ 設定")

        # API Key確認
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            st.success("✅ GOOGLE_API_KEY 設定済み")
        else:
            st.error("❌ GOOGLE_API_KEY が未設定")
            st.info("`.env`ファイルに設定するか、環境変数を設定してください。")
            st.stop()

        # プロンプトパターン選択
        st.subheader("プロンプトパターン")
        pattern = st.selectbox(
            "生成パターンを選択",
            options=["口パク動画（Talking Video）", "通常動画（書籍表紙の動き）"],
            index=0,
            help="口パク: 人物が話す動画 / 通常: 書籍表紙がズームやパンする動画"
        )

        # 動画生成パラメータ
        st.subheader("動画設定")

        # パターンに応じて設定を変更
        if pattern == "口パク動画（Talking Video）":
            st.info("💬 Talking Video: 約8秒の口パク動画を生成します")
            duration = 8  # 固定
        else:
            duration = st.selectbox(
                "動画の長さ（秒）",
                options=[4, 6, 8],
                index=2,
                help="生成する動画の長さを選択"
            )

        output_dir = st.text_input(
            "出力ディレクトリ",
            value="output",
            help="生成された動画の保存先"
        )

    # メインコンテンツ
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("📤 入力")

        # 画像アップロード（パターンに応じてラベルを変更）
        if pattern == "口パク動画（Talking Video）":
            upload_label = "人物画像をアップロード"
            upload_help = "人物が写っている画像をアップロードしてください（口パク動画を生成します）"
        else:
            upload_label = "書籍表紙画像をアップロード"
            upload_help = "書籍表紙や商品画像をアップロードしてください"

        uploaded_file = st.file_uploader(
            upload_label,
            type=["png", "jpg", "jpeg"],
            help=upload_help
        )

        if uploaded_file:
            st.image(uploaded_file, caption="アップロードされた画像", use_container_width=True)

        # プロンプトテンプレート（パターンに応じて変更）
        if pattern == "口パク動画（Talking Video）":
            default_prompt = (
                "ショット: 正面のバストショット。カメラは固定し、揺れや過度なズームは避ける。\n"
                "被写体: 入力画像の人物。顔の造形・髪型・衣服の一貫性を保つ。自然な瞬きと微細な表情。\n"
                "口の動き: セリフと正確に同期。過度な頭の揺れを避ける。\n"
                "会話: 「記憶力の低下、不眠、うつ、発達障害、肥満、高血圧、糖尿病、感染症の重症化……すべての不調は腸から始まる!」\n"
                "発話かな: 「きおくりょくのていか、ふみん、うつ、はったつしょうがい、ひまん、こうけつあつ、とうにょうびょう、かんせんしょうのじゅうしょうか……すべてのふちょうはちょうからはじまる！」\n"
                "表示: 字幕は表示しない。フリッカーや歪みを避け、実写的でクリアな質感。約8秒。"
            )
            prompt_help = "口パク動画のプロンプト（会話の文章と発話かなを含めてください）"
            prompt_height = 200
        else:
            default_prompt = "本のタイトルが浮かび上がる。カメラがゆっくりと本に近づいていく。"
            prompt_help = "動画生成の指示を入力してください（例: カメラが本に近づく、タイトルが輝く）"
            prompt_height = 100

        # プロンプト入力
        prompt = st.text_area(
            "動画生成プロンプト",
            value=default_prompt,
            height=prompt_height,
            help=prompt_help
        )

        # 生成ボタン
        generate_button = st.button(
            "🎥 動画を生成",
            type="primary",
            disabled=(uploaded_file is None or not prompt.strip()),
            use_container_width=True
        )

    with col2:
        st.header("📥 出力")

        if generate_button and uploaded_file and prompt.strip():
            # 一時ファイルに保存
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)
            temp_image_path = temp_dir / uploaded_file.name

            with open(temp_image_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                # 動画生成（進捗表示付き）
                with st.spinner("⏳ 動画を生成中... 数分かかる場合があります"):
                    # パターンに応じて適切な関数を呼び出し
                    if pattern == "口パク動画（Talking Video）":
                        st.info("🎥 Veo 3.0 Talking Video APIで動画生成を開始しました")
                        output_path = generate_video_talking(
                            image_path=temp_image_path,
                            prompt=prompt,
                            output_dir=Path(output_dir),
                            model="veo-3.0-generate-001"
                        )
                    else:
                        st.info("🎥 Veo 3.1 APIで動画生成を開始しました")
                        output_path = generate_video_simple(
                            image_path=temp_image_path,
                            prompt=prompt,
                            output_dir=Path(output_dir),
                            duration=duration
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
                            use_container_width=True
                        )

                    # ファイル情報
                    file_size_mb = output_path.stat().st_size / (1024 * 1024)
                    st.info(f"ファイルサイズ: {file_size_mb:.2f} MB")

            except FileNotFoundError as e:
                st.error(f"❌ エラー: {e}")
                st.info("画像ファイルが見つかりません")

            except ValueError as e:
                st.error(f"❌ エラー: {e}")
                st.info("パラメータが正しくありません")

            except SystemExit as e:
                st.error(f"❌ エラー: {e}")
                st.info("API呼び出しに失敗しました。API Keyやクオータを確認してください")

            except Exception as e:
                st.error(f"❌ 予期しないエラー: {e}")
                st.exception(e)

            finally:
                # 一時ファイル削除
                if temp_image_path.exists():
                    temp_image_path.unlink()

        elif not uploaded_file:
            if pattern == "口パク動画（Talking Video）":
                st.info("👆 人物画像をアップロードしてください")
            else:
                st.info("👆 書籍表紙画像をアップロードしてください")

        elif not prompt.strip():
            st.warning("⚠️ プロンプトを入力してください")

    # フッター
    st.markdown("---")
    st.markdown(
        "📖 [仕様書](SPEC.md) | "
        "🔧 [開発原則](CLAUDE.md) | "
        "🌳 [Git運用フロー](docs/git-workflow.md)"
    )


if __name__ == "__main__":
    main()
