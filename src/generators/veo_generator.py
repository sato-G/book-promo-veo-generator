#!/usr/bin/env python3
"""
Veo 3.1動画ジェネレーター
静止画から動画を生成
"""
import os
import time
import shutil
from pathlib import Path
from google import genai
from google.genai import types


class VeoGenerator:
    """Veo 3.1を使った動画生成"""

    def __init__(self, api_key: str = None):
        """
        初期化

        Args:
            api_key: Google API Key (Noneの場合は環境変数から取得)
        """
        if api_key:
            os.environ['GOOGLE_API_KEY'] = api_key
        elif 'GOOGLE_API_KEY' not in os.environ:
            raise ValueError("GOOGLE_API_KEY is not set")

        self.client = genai.Client(api_key=os.environ['GOOGLE_API_KEY'])

    def generate_video(
        self,
        image_path: Path,
        output_path: Path,
        prompt: str,
        timeout: int = 300
    ) -> Path:
        """
        画像から動画を生成

        Args:
            image_path: 入力画像パス
            output_path: 出力動画パス
            prompt: 生成プロンプト
            timeout: タイムアウト（秒）

        Returns:
            生成された動画のパス
        """
        print(f"🎥 Veo 3.1で動画生成中...")
        print(f"   入力: {image_path.name}")

        # ASCII文字のみのパスにコピー（Unicode対策）
        tmp_dir = output_path.parent / "tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        tmp_img = tmp_dir / f"input_{int(time.time())}.jpg"
        shutil.copy(str(image_path), str(tmp_img))

        # 画像データを読み込み
        with open(tmp_img, 'rb') as f:
            image_bytes = f.read()

        # Veo 3.1で動画生成
        image = types.Image(imageBytes=image_bytes, mimeType='image/jpeg')
        reference_image = types.VideoGenerationReferenceImage(image=image)

        print(f"   プロンプト: {prompt[:80]}...")

        operation = self.client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                reference_images=[reference_image]
            )
        )

        print("   ⏳ 生成中...")

        # ポーリング
        start_time = time.time()
        while not operation.done:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Veo 3.1 generation timed out after {timeout}s")

            time.sleep(10)
            operation = self.client.operations.get(operation)
            print("   ⏳ 生成中...")

        print("   ✓ 生成完了！")

        # ダウンロード
        generated_video = operation.response.generated_videos[0]
        self.client.files.download(file=generated_video.video)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        generated_video.video.save(str(output_path))

        # 一時ファイルを削除
        tmp_img.unlink()

        print(f"   💾 保存: {output_path}")
        return output_path

    @staticmethod
    def create_prompt_for_scene(scene_type: str, custom_details: str = "") -> str:
        """
        シーンタイプに応じたプロンプトを生成

        Args:
            scene_type: "marching", "meeting", "portrait"など
            custom_details: カスタム詳細

        Returns:
            生成プロンプト
        """
        prompts = {
            "marching": """Historical soldiers marching forward in formation.
The soldiers are walking with synchronized steps, their rifles moving rhythmically.
Subtle forward motion as they march. Documentary style, realistic military march.
Maintain the historical authenticity. No added elements. 8 seconds.""",

            "meeting": """Historical wartime meeting scene with subtle realistic movements.
The people seated at the formal meeting are having a serious discussion.
Subtle head movements, slight gestures, and facial expressions showing gravity of the situation.
Documentary style, realistic historical atmosphere.
Camera remains steady. Maintain the formal historical tone. 8 seconds.""",

            "portrait": """A dramatic slow camera push-in on this historical photograph.
The camera slowly zooms in with cinematic depth.
Subtle lighting shifts add drama. No added objects or text.
Maintain the somber historical tone. 8 seconds.""",

            "custom": custom_details
        }

        return prompts.get(scene_type, prompts["custom"])
