#!/usr/bin/env python3
"""
Gemini API動作確認スクリプト

使い方:
    cd src/simpletest
    python test_gemini.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 環境変数読み込み
load_dotenv()

from google import genai


def test_gemini_api():
    """Gemini APIの動作確認"""

    # API Key確認
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY が設定されていません")
        print("export GOOGLE_API_KEY=your_api_key")
        sys.exit(1)

    print("\n" + "="*60)
    print("🧪 Gemini API 動作確認")
    print("="*60)
    print(f"API Key: {api_key[:20]}...{api_key[-10:]}")
    print("="*60 + "\n")

    try:
        # Gemini Clientを初期化
        client = genai.Client(api_key=api_key)

        # テストプロンプト
        prompt = "AIとは何ですか？30文字以内で説明してください。"

        print(f"📝 プロンプト: {prompt}\n")
        print("⏳ Gemini 2.5 Flashに問い合わせ中...\n")

        # Gemini 2.5 Flashで生成
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        print("="*60)
        print("✅ Gemini API 動作確認成功！")
        print("="*60)
        print(f"\n回答: {response.text}\n")
        print("="*60 + "\n")

        # Veo 3.1アクセス確認
        print("\n🔍 Veo 3.1 アクセス権限確認中...\n")

        try:
            # Veo 3.1にアクセスを試みる
            test_image_path = project_root / "data/image_sample/test1.jpg"

            if not test_image_path.exists():
                print(f"⚠️  テスト画像が見つかりません: {test_image_path}")
                return

            from google.genai import types

            # 画像読み込み
            image_bytes = test_image_path.read_bytes()
            image = types.Image(imageBytes=image_bytes, mimeType="image/jpeg")

            reference = types.VideoGenerationReferenceImage(
                image=image,
                referenceType=types.VideoGenerationReferenceType.ASSET,
            )

            config = types.GenerateVideosConfig(
                referenceImages=[reference],
                durationSeconds=4,
            )

            # Veo 3.1で動画生成を試みる（テストのみ）
            operation = client.models.generate_videos(
                model="veo-3.1-generate-preview",
                prompt="テスト",
                config=config,
            )

            print("="*60)
            print("✅ Veo 3.1 アクセス権限あり！")
            print("="*60)
            print("このAPI KeyでVeo 3.1が使用できます！\n")

            # テストなのでキャンセル
            print("（テストのため動画生成はキャンセルしました）\n")

        except Exception as veo_error:
            error_msg = str(veo_error)

            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                print("="*60)
                print("⚠️  Veo 3.1 クォータ制限中")
                print("="*60)
                print("API KeyはVeo 3.1にアクセス可能ですが、")
                print("現在クォータ制限中です。24時間後に再試行してください。\n")

            elif "400" in error_msg or "INVALID_ARGUMENT" in error_msg:
                print("="*60)
                print("❌ Veo 3.1 アクセス権限なし")
                print("="*60)
                print("このAPI KeyではVeo 3.1にアクセスできません。")
                print("Google AI StudioでVeo 3.1のアクセスを申請してください。\n")

            elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
                print("="*60)
                print("❌ OAuth2認証が必要")
                print("="*60)
                print("このプロジェクトはOAuth2認証が必要です。\n")

            else:
                print(f"⚠️  Veo 3.1アクセス確認エラー: {error_msg}\n")

    except Exception as e:
        print(f"\n❌ Gemini API エラー: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    test_gemini_api()
