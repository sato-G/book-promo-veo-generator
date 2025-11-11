#!/usr/bin/env python3
"""
OpenAI API を使ったナレーション生成クライアント

書籍プロモーション動画用の質の高いナレーションテキストを生成
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

# .envから環境変数を読み込む
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenvがなければ環境変数から直接読み込む

try:
    from openai import OpenAI
except ImportError:
    raise ImportError(
        "openai is not installed. "
        "Please run: pip install openai"
    )


@dataclass
class BookInfo:
    """書籍情報"""
    title: str
    description: str
    target_audience: str = "一般読者"
    mood: str = "エネルギッシュ"


class ScenarioGenerator:
    """OpenAI APIを使ったナレーション生成クライアント"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """
        初期化

        Args:
            api_key: OpenAI API Key (Noneの場合は.envまたは環境変数から取得)
            model: 使用するモデル (gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, o1, o1-preview, o1-mini, gpt-5, gpt-5-miniなど)
        """
        # API Keyの設定
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "OpenAI API Key が設定されていません。\n"
                ".envファイルに OPENAI_API_KEY を設定するか、\n"
                "環境変数 OPENAI_API_KEY を設定してください。"
            )

        # OpenAI クライアントを初期化
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

        print(f"✓ OpenAI APIクライアント初期化完了 (model: {model})")

    def generate_narration(
        self,
        book_info: BookInfo,
        language: str = "ja",
        target_length: int = 55
    ) -> str:
        """
        書籍プロモーション動画用のナレーションテキストを生成

        Args:
            book_info: 書籍情報
            language: 言語 (ja/en)
            target_length: 目標文字数（デフォルト: 55文字）

        Returns:
            ナレーションテキスト
        """
        print("\n" + "=" * 60)
        print("🤖 ナレーション生成開始")
        print("=" * 60)
        print(f"📖 書籍: {book_info.title}")
        print(f"🎯 ターゲット: {book_info.target_audience}")
        print(f"🎨 雰囲気: {book_info.mood}")
        print("=" * 60 + "\n")

        # プロンプトを生成
        system_prompt = self._create_system_prompt(language, target_length)
        user_prompt = self._create_user_prompt(book_info, language)

        try:
            print("📤 OpenAI API呼び出し中...")

            # シンプルなプロンプト（システムとユーザーを統合）
            combined_prompt = f"""{system_prompt}

{user_prompt}"""

            # 最小限のパラメータのみ
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": combined_prompt}]
            )

            print("✓ API呼び出し完了")

            # レスポンスを取得（そのまま使用）
            narration_text = response.choices[0].message.content
            if narration_text:
                narration_text = narration_text.strip()
            else:
                narration_text = ""

            # 結果を表示
            print("\n" + "=" * 60)
            print("✅ ナレーション生成完了")
            print("=" * 60)
            print(f"\n📝 ナレーションテキスト ({len(narration_text)}文字):")
            print(f"\n   「{narration_text}」\n")
            print(f"💡 最初の20文字: 「{narration_text[:20]}」")
            print("=" * 60 + "\n")

            return narration_text

        except Exception as e:
            print(f"❌ エラー: {e}")
            raise

    def _create_system_prompt(self, language: str, target_length: int = 55) -> str:
        """システムプロンプトを生成（シンプル版）"""
        min_length = max(20, target_length - 10)
        max_length = min(100, target_length + 10)

        if language == "ja":
            return f"""あなたは書籍プロモーション動画のプロフェッショナルなコピーライターです。

8秒のショート動画用のナレーションテキストを作成してください。

条件:
- 文字数: {min_length}〜{max_length}文字
- 最初の20文字で視聴者の注意を引きつける
- シンプルで力強い日本語
- 問いかけや驚きで始める

ナレーションテキストのみを出力してください。"""
        else:
            return f"""You are a professional copywriter for book promotional videos.

Create a narration for an 8-second short video.

Requirements:
- {min_length}-{max_length} characters
- First 20 characters must grab attention
- Simple and powerful
- Start with a question or surprise

Output only the narration text."""

    def _create_user_prompt(self, book_info: BookInfo, language: str) -> str:
        """ユーザープロンプトを生成（シンプル版）"""
        if language == "ja":
            return f"""書籍情報:
タイトル: {book_info.title}
説明: {book_info.description}
ターゲット読者: {book_info.target_audience}
雰囲気: {book_info.mood}"""
        else:
            return f"""Book:
Title: {book_info.title}
Description: {book_info.description}
Target: {book_info.target_audience}
Mood: {book_info.mood}"""


def main():
    """CLI実行用のメイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='書籍プロモーション動画ナレーション生成')
    parser.add_argument('--title', '-t', type=str, required=True,
                       help='書籍タイトル')
    parser.add_argument('--description', '-d', type=str, required=True,
                       help='書籍の説明')
    parser.add_argument('--target', type=str, default='一般読者',
                       help='ターゲット読者')
    parser.add_argument('--mood', type=str, default='エネルギッシュ',
                       help='動画の雰囲気')
    parser.add_argument('--model', type=str, default='gpt-4o',
                       help='OpenAIモデル (gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-4, o1, o1-preview, o1-mini, gpt-5, gpt-5-miniなど)')
    parser.add_argument('--language', type=str, default='ja',
                       choices=['ja', 'en'],
                       help='言語')

    args = parser.parse_args()

    # 書籍情報を作成
    book_info = BookInfo(
        title=args.title,
        description=args.description,
        target_audience=args.target,
        mood=args.mood
    )

    # ナレーション生成クライアントを作成
    generator = ScenarioGenerator(model=args.model)

    # ナレーションを生成
    narration = generator.generate_narration(book_info, language=args.language)

    print(f"\n生成されたナレーション:\n{narration}")


if __name__ == '__main__':
    main()
