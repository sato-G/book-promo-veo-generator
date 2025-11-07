#!/usr/bin/env python3
"""
Veo 3.0 (text-to-video) テストスクリプト

使い方:
    cd src/simpletest
    python test_veo3_text.py
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# プロジェクトルートをPythonパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 環境変数読み込み
load_dotenv()

from google import genai
from google.genai import types


# ========================================
# テスト設定（ここを編集）
# ========================================
TEST_PROMPT = "a close-up shot of a golden retriever playing in a field of sunflowers"
NEGATIVE_PROMPT = "barking, woofing"
OUTPUT_DIR = project_root / "data/output"
# ========================================


def test_veo3_text_to_video():
    """Veo 3.0でテキストから動画生成"""

    # API Key確認
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY が設定されていません")
        print("export GOOGLE_API_KEY=your_api_key")
        sys.exit(1)

    print("\n" + "="*60)
    print("🧪 Veo 3.0 (text-to-video) テスト")
    print("="*60)
    print(f"プロンプト: {TEST_PROMPT}")
    print(f"ネガティブプロンプト: {NEGATIVE_PROMPT}")
    print("="*60 + "\n")

    try:
        client = genai.Client(api_key=api_key)

        print("⏳ Veo 3.0で動画生成を開始...\n")

        operation = client.models.generate_videos(
            model="veo-3.0-generate-preview",
            prompt=TEST_PROMPT,
            config=types.GenerateVideosConfig(
                negative_prompt=NEGATIVE_PROMPT,
            ),
        )

        # 動画生成完了まで待機
        wait_count = 0
        while not operation.done:
            wait_count += 1
            print(f"⏳ 生成中... ({wait_count * 20}秒経過)")
            time.sleep(20)
            operation = client.operations.get(operation)

        print("\n✅ 動画生成完了！\n")

        # 生成された動画を取得
        generated_video = operation.result.generated_videos[0]
        client.files.download(file=generated_video.video)

        # 出力ファイル保存
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = OUTPUT_DIR / f"veo3_text_{timestamp}.mp4"

        generated_video.video.save(str(output_path))

        print("="*60)
        print("✅ テスト成功！")
        print("="*60)
        print(f"動画: {output_path}")
        print(f"サイズ: {output_path.stat().st_size / (1024*1024):.2f} MB")
        print("="*60 + "\n")

    except Exception as e:
        error_msg = str(e)

        print("\n" + "="*60)
        print("❌ テスト失敗")
        print("="*60)
        print(f"エラー: {error_msg}\n")

        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            print("⚠️  クォータ制限中です。24時間後に再試行してください。")
        elif "400" in error_msg or "INVALID_ARGUMENT" in error_msg:
            print("⚠️  このAPI KeyではVeo 3.0にアクセスできません。")
            print("有料プランへのアップグレードが必要な可能性があります。")
        elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
            print("⚠️  認証エラーです。API Keyを確認してください。")

        sys.exit(1)


if __name__ == "__main__":
    test_veo3_text_to_video()
