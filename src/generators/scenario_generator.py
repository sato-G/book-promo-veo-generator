#!/usr/bin/env python3
"""
OpenAI API を使ったナレーション生成クライアント

書籍プロモーション動画用の質の高いナレーションテキストを生成
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
import json

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
        language: str = "ja"
    ) -> str:
        """
        書籍プロモーション動画用のナレーションテキストを生成

        Args:
            book_info: 書籍情報
            language: 言語 (ja/en)

        Returns:
            ナレーションテキスト（50〜60文字、8秒で読める長さ）
        """
        print("\n" + "=" * 60)
        print("🤖 ナレーション生成開始")
        print("=" * 60)
        print(f"📖 書籍: {book_info.title}")
        print(f"🎯 ターゲット: {book_info.target_audience}")
        print(f"🎨 雰囲気: {book_info.mood}")
        print("=" * 60 + "\n")

        # プロンプトを生成
        system_prompt = self._create_system_prompt(language)
        user_prompt = self._create_user_prompt(book_info, language)

        try:
            print("📤 OpenAI API呼び出し中...")

            # APIパラメータを準備
            api_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
            }

            # モデルに応じてパラメータを選択
            # gpt-5, o1シリーズは制限が多い（temperature, response_formatなし）
            if self.model.startswith("gpt-5") or self.model.startswith("o1"):
                api_params["max_completion_tokens"] = 200
                # temperature は使えない（デフォルト=1のみ）
            else:
                api_params["temperature"] = 0.9
                api_params["max_tokens"] = 200
                api_params["response_format"] = {"type": "json_object"}

            # API呼び出し
            response = self.client.chat.completions.create(**api_params)

            print("✓ API呼び出し完了")

            # レスポンスを取得
            narration_text = response.choices[0].message.content.strip()

            # マークダウンコードフェンスを削除
            if narration_text.startswith("```"):
                lines = narration_text.split("\n")
                # 最初と最後の行（コードフェンス）を削除
                narration_text = "\n".join(lines[1:-1]).strip()

            # JSON形式の場合はパース
            if narration_text.startswith("{") and "narration_text" in narration_text:
                try:
                    result_json = json.loads(narration_text)
                    narration_text = result_json.get("narration_text", narration_text)
                except json.JSONDecodeError:
                    pass  # JSONでない場合はそのまま使用

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

    def _create_system_prompt(self, language: str) -> str:
        """システムプロンプトを生成"""
        if language == "ja":
            return """あなたは書籍プロモーション動画のプロフェッショナルなコピーライターです。

**ミッション**: 8秒のショート動画用の「読まれるナレーションテキスト」を作成すること

**絶対に守るべきルール**:

1. **文字数**: 50〜60文字厳守（8秒で読める長さ）
2. **最初の20文字が最重要**: 視聴者の注意を一瞬で引きつける
3. **構成**:
   - 冒頭: 強烈なフック（問いかけ、驚き、共感）
   - 中盤: 書籍の核心的価値
   - 結び: 行動を促す/期待を高める

4. **文体**:
   - シンプルで力強い日本語
   - 読みやすいリズム
   - 句読点を効果的に使う

5. **避けるべきこと**:
   - 抽象的すぎる表現
   - 長すぎる文
   - ありきたりなフレーズ

**出力形式**:
```json
{
  "narration_text": "ここにナレーションテキスト（50-60文字）"
}
```

**例**:
- 良い例: 「成功する人は何が違う？この本に答えがある。今すぐ読もう。」（30文字）
- 悪い例: 「本書は成功するための様々なノウハウを提供する一冊となっております。」（抽象的で弱い）"""
        else:
            return """You are a professional copywriter for book promotional videos.

**Mission**: Create a "narration script" for 8-second short videos

**Strict Rules**:

1. **Character Count**: 50-60 characters (readable in 8 seconds)
2. **First 20 characters are critical**: Instantly grab viewer attention
3. **Structure**:
   - Opening: Strong hook (question, surprise, empathy)
   - Middle: Core book value
   - Closing: Call to action / build anticipation

4. **Style**:
   - Simple and powerful language
   - Easy-to-read rhythm
   - Effective use of punctuation

5. **Avoid**:
   - Overly abstract expressions
   - Too-long sentences
   - Clichéd phrases

**Output Format**:
```json
{
  "narration_text": "Narration text here (50-60 chars)"
}
```"""

    def _create_user_prompt(self, book_info: BookInfo, language: str) -> str:
        """ユーザープロンプトを生成"""
        if language == "ja":
            return f"""以下の書籍のプロモーション動画用ナレーションテキストを作成してください。

# 書籍情報
- **タイトル**: {book_info.title}
- **説明**: {book_info.description}
- **ターゲット読者**: {book_info.target_audience}
- **動画の雰囲気**: {book_info.mood}

# 要求事項
- 文字数: 50〜60文字
- 最初の20文字で視聴者の心を掴む
- 8秒で読み切れる自然なリズム

必ずJSON形式で、narration_textキーに50-60文字のテキストを返してください。"""
        else:
            return f"""Create a promotional video narration for the following book.

# Book Information
- **Title**: {book_info.title}
- **Description**: {book_info.description}
- **Target Audience**: {book_info.target_audience}
- **Video Mood**: {book_info.mood}

# Requirements
- Character count: 50-60 characters
- First 20 characters must grab attention
- Natural rhythm readable in 8 seconds

Return JSON format with narration_text key containing 50-60 character text."""


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
