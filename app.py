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

# generators/veo3_sample.pyをインポート
sys.path.insert(0, str(Path(__file__).parent))
from generators.veo3_sample import generate_video


def main():
    """Streamlit メインアプリケーション"""

    st.set_page_config(
        page_title="書籍プロモーション動画生成",
        page_icon="📚",
        layout="wide"
    )

    st.title("📚 書籍プロモーション動画生成")
    st.markdown("Google Veo 3.1を使って、書籍表紙画像から自動でプロモーション動画を生成します。")

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

        # 動画生成パラメータ
        st.subheader("動画設定")
        duration = st.selectbox(
            "動画の長さ（秒）",
            options=[4, 6, 8],
            index=2,  # デフォルト8秒
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

        # 画像アップロード
        uploaded_file = st.file_uploader(
            "書籍表紙画像をアップロード",
            type=["png", "jpg", "jpeg"],
            help="PNGまたはJPEG形式の画像をアップロードしてください"
        )

        if uploaded_file:
            st.image(uploaded_file, caption="アップロードされた画像", use_container_width=True)

        # プロンプト入力
        prompt = st.text_area(
            "動画生成プロンプト",
            value="本のタイトルが浮かび上がる",
            height=100,
            help="動画生成の指示を入力してください（例: カメラが本に近づく、タイトルが輝く）"
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
                    st.info("🎥 Veo 3.1 APIで動画生成を開始しました")

                    # veo3_sample.pyのgenerate_video関数を呼び出し
                    output_path = generate_video(
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
