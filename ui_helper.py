#!/usr/bin/env python3
"""
Streamlit UI用のヘルパーモジュール

動画生成ロジックをカプセル化し、UIから簡単に呼び出せるようにする。
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# generators/veo3_sample.pyをインポート
sys.path.insert(0, str(Path(__file__).parent))
from generators.veo3_sample import generate_video as veo_generate_video


def check_api_key() -> tuple[bool, str]:
    """
    API Keyの設定を確認

    Returns:
        (bool, str): (設定されているか, API Key or エラーメッセージ)
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        return True, api_key
    else:
        return False, "GOOGLE_API_KEY が未設定です"


def generate_video_from_upload(
    uploaded_file,
    prompt: str,
    duration: int,
    output_dir: Path = Path("output")
) -> Path:
    """
    アップロードされた画像から動画を生成

    Args:
        uploaded_file: Streamlitのアップロードファイルオブジェクト
        prompt: 動画生成プロンプト
        duration: 動画の長さ（秒）
        output_dir: 出力ディレクトリ

    Returns:
        生成された動画ファイルのパス

    Raises:
        Exception: 動画生成中のエラー
    """
    # 一時ファイルに保存
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    temp_image_path = temp_dir / uploaded_file.name

    try:
        # アップロードされた画像を保存
        with open(temp_image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # 動画生成
        output_path = veo_generate_video(
            image_path=temp_image_path,
            prompt=prompt,
            output_dir=output_dir,
            duration=duration,
        )

        return output_path

    finally:
        # 一時ファイル削除
        if temp_image_path.exists():
            temp_image_path.unlink()
