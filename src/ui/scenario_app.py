#!/usr/bin/env python3
"""
ナレーション生成 Streamlit UI

書籍情報から8秒動画用の質の高いナレーションテキストを生成
"""

import streamlit as st
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.generators.scenario_generator import ScenarioGenerator, BookInfo


def main():
    """Streamlit UIのメイン関数"""

    st.set_page_config(
        page_title="ナレーション生成AI",
        page_icon="🤖",
        layout="centered"
    )

    st.title("🤖 プロモーション動画ナレーション生成AI")
    st.markdown("OpenAI GPT-4o/GPT-5 で、8秒ショート動画用の質の高いナレーションテキストを生成します")

    # API Key確認
    import os
    from dotenv import load_dotenv
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("✅ OpenAI API Key設定済み (.envから読み込み)")
    else:
        st.error("❌ OPENAI_API_KEY が設定されていません")
        st.info("`.env`ファイルに `OPENAI_API_KEY=your-api-key` を追加してください")
        st.stop()

    st.markdown("---")

    # 入力フォーム
    st.header("📖 書籍情報入力")

    book_title = st.text_input(
        "書籍タイトル *",
        placeholder="例: AI時代の未来戦略",
        help="プロモーションする書籍のタイトルを入力してください"
    )

    book_description = st.text_area(
        "書籍の説明 *",
        height=120,
        placeholder="例: AIとビジネスの未来を探る一冊。最新技術から実践的な活用法まで、あなたのビジネスを変革するヒントが満載です。",
        help="書籍の内容を簡潔に説明してください（2〜3文程度）"
    )

    promo_style = st.text_input(
        "宣伝スタイル（オプション）",
        placeholder="例: 大袈裟に表現、丁寧に表現、ユーモラスに、情熱的に、落ち着いて",
        help="ナレーションの表現スタイルを指定できます（未入力でも可）"
    )

    col1, col2 = st.columns(2)

    with col1:
        target_audience = st.text_input(
            "ターゲット読者",
            value="一般読者",
            placeholder="例: ビジネスパーソン、学生、技術者",
            help="どのような読者層を想定していますか？"
        )

    with col2:
        mood_options = [
            "エネルギッシュ",
            "落ち着いた",
            "ミステリアス",
            "知的",
            "感動的",
            "ユーモラス"
        ]
        mood = st.selectbox(
            "動画の雰囲気",
            options=mood_options,
            index=0,
            help="動画全体の雰囲気を選択してください"
        )

    # モデル選択
    st.markdown("### ⚙️ AI設定")
    model_col1, model_col2 = st.columns([2, 1])

    with model_col1:
        model_options = [
            "gpt-5-chat-latest",
            "gpt-4o"
        ]
        model = st.selectbox(
            "AIモデル",
            options=model_options,
            index=0,
            help="gpt-5-chat-latest: GPT-5最新チャットモデル（推奨） / gpt-4o: GPT-4o高品質"
        )

    with model_col2:
        target_length = st.number_input(
            "目標文字数",
            min_value=20,
            max_value=100,
            value=55,
            step=5,
            help="生成するナレーションの目標文字数"
        )

    st.markdown("---")

    # 生成ボタン
    can_generate = book_title.strip() and book_description.strip()

    if st.button(
        "🤖 ナレーションを生成",
        disabled=not can_generate,
        type="primary",
        use_container_width=True
    ):
        if not can_generate:
            st.error("書籍タイトルと説明を入力してください")
            return

        try:
            # BookInfo作成（宣伝スタイルを説明に追加）
            description_with_style = book_description
            if promo_style.strip():
                description_with_style = f"{book_description}\n\n【宣伝スタイル】{promo_style}"

            book_info = BookInfo(
                title=book_title,
                description=description_with_style,
                target_audience=target_audience,
                mood=mood
            )

            # ナレーション生成
            with st.spinner("🤖 AIがナレーションを生成中... 10〜30秒ほどかかります"):
                generator = ScenarioGenerator(model=model)
                narration_text = generator.generate_narration(book_info, language="ja", target_length=target_length)

            st.success("✅ ナレーション生成完了！")

            # 結果をsession_stateに保存
            st.session_state.narration_text = narration_text
            st.session_state.book_info = book_info
            st.session_state.target_length = target_length
            st.session_state.model = model

        except Exception as e:
            st.error(f"❌ エラー: {e}")
            st.exception(e)

    # 生成結果を表示
    if 'narration_text' in st.session_state:
        narration_text = st.session_state.narration_text

        st.markdown("---")
        st.header("📋 生成されたナレーション")

        # ナレーション表示（大きく）
        st.markdown(f"### 「{narration_text}」")

        # 統計情報
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("文字数", f"{len(narration_text)}文字")
        with col2:
            first_20 = narration_text[:20] if len(narration_text) >= 20 else narration_text
            st.metric("最初の20文字", f"「{first_20}」")
        with col3:
            estimated_seconds = len(narration_text) / 7  # 約7文字/秒
            st.metric("推定読み上げ時間", f"{estimated_seconds:.1f}秒")

        # テキストエリアでコピー可能に
        st.text_area(
            "ナレーションテキスト（コピー用）",
            value=narration_text,
            height=100,
            help="このテキストをコピーして、スライドショー生成などに使用できます"
        )

        st.markdown("---")

        # 次のステップ
        st.info("💡 このナレーションを使ってスライドショー動画を生成できます！")
        st.caption("スライドショー生成: http://localhost:8502")

    # 使い方の説明
    with st.expander("📖 使い方"):
        st.markdown("""
        ### ナレーション生成AIの使い方

        **1. 書籍情報を入力**
        - タイトルと説明を入力（必須）
        - ターゲット読者と雰囲気を選択

        **2. AIモデルを選択**
        - gpt-4o: 高品質な出力（推奨）
        - gpt-4o-mini: 高速・低コスト
        - gpt-4-turbo / gpt-4: GPT-4シリーズ
        - o1 / o1-preview / o1-mini: 推論特化モデル
        - gpt-5 / gpt-5-mini: 最新モデル（利用可能な場合）

        **3. ナレーションを生成**
        - 「ナレーションを生成」ボタンをクリック
        - AIが10〜30秒で最適なナレーションを生成

        **4. 結果を確認**
        - 文字数: 50〜60文字（8秒で読める長さ）
        - 最初の20文字: 視聴者の注意を引きつけるフック
        - 推定読み上げ時間: 実際にかかる秒数

        ### プロンプトエンジニアリングのポイント

        このAIは以下の点に特化しています：

        - **最初の20文字**: 視聴者の注意を一瞬で引きつける
        - **シンプルで力強い**: 抽象的な表現を避け、明確なメッセージ
        - **8秒で完結**: 自然なリズムで読み切れる長さ
        - **行動を促す**: 読者が「読みたい」と思う結び

        ### 次のステップ

        生成されたナレーションをコピーして：
        - スライドショー動画生成に使用
        - Veo3で動画に変換
        - 手動で編集・調整
        """)


if __name__ == "__main__":
    main()
