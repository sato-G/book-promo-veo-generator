#!/usr/bin/env python3
"""
Google Cloud Text-to-Speech API クライアント

テキストから音声を生成
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Literal
from dataclasses import dataclass

try:
    from google.cloud import texttospeech
except ImportError:
    raise ImportError(
        "google-cloud-texttospeech is not installed. "
        "Please run: pip install google-cloud-texttospeech"
    )


# 音声の性別
VoiceGender = Literal["NEUTRAL", "MALE", "FEMALE"]

# オーディオエンコーディング
AudioEncoding = Literal["MP3", "LINEAR16", "OGG_OPUS"]


@dataclass
class TTSConfig:
    """Text-to-Speech設定"""
    text: str
    language_code: str = "ja-JP"  # デフォルトは日本語
    voice_name: Optional[str] = None
    voice_gender: VoiceGender = "NEUTRAL"
    audio_encoding: AudioEncoding = "MP3"
    speaking_rate: float = 1.0  # 0.25 - 4.0
    pitch: float = 0.0  # -20.0 - 20.0
    volume_gain_db: float = 0.0  # -96.0 - 16.0


class TextToSpeechClient:
    """Google Cloud Text-to-Speech APIクライアント"""

    # 日本語の音声一覧
    JAPANESE_VOICES = {
        "female_a": "ja-JP-Neural2-B",  # 女性A（ニューラル）
        "male_a": "ja-JP-Neural2-C",    # 男性A（ニューラル）
        "male_b": "ja-JP-Neural2-D",    # 男性B（ニューラル）
        "female_b": "ja-JP-Wavenet-A",  # 女性B（Wavenet）
        "male_c": "ja-JP-Wavenet-C",    # 男性C（Wavenet）
    }

    # 英語の音声一覧
    ENGLISH_VOICES = {
        "female_a": "en-US-Neural2-C",   # 女性A（ニューラル）
        "female_b": "en-US-Neural2-E",   # 女性B（ニューラル）
        "female_c": "en-US-Neural2-F",   # 女性C（ニューラル）
        "female_d": "en-US-Neural2-G",   # 女性D（ニューラル）
        "female_e": "en-US-Neural2-H",   # 女性E（ニューラル）
        "male_a": "en-US-Neural2-A",     # 男性A（ニューラル）
        "male_b": "en-US-Neural2-D",     # 男性B（ニューラル）
        "male_c": "en-US-Neural2-I",     # 男性C（ニューラル）
        "male_d": "en-US-Neural2-J",     # 男性D（ニューラル）
    }

    def __init__(self, credentials_path: Optional[str] = None):
        """
        初期化

        Args:
            credentials_path: Google Cloud認証情報のパス（Noneの場合は環境変数から取得）
        """
        # 認証情報のパスを設定
        if credentials_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        # クライアントを初期化
        try:
            self.client = texttospeech.TextToSpeechClient()
            print("✓ Text-to-Speech APIクライアント初期化完了")
        except Exception as e:
            raise Exception(
                f"Text-to-Speech APIクライアントの初期化に失敗: {e}\n"
                f"認証情報を確認してください。\n"
                f"  1. Google Cloudプロジェクトでサービスを有効化\n"
                f"  2. gcloud auth application-default login を実行\n"
                f"  または、GOOGLE_APPLICATION_CREDENTIALS環境変数を設定"
            )

    def synthesize_speech(
        self,
        text: str,
        output_path: Optional[Path] = None,
        output_name: str = "speech",
        language_code: str = "ja-JP",
        voice_name: Optional[str] = None,
        voice_gender: VoiceGender = "NEUTRAL",
        audio_encoding: AudioEncoding = "MP3",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        volume_gain_db: float = 0.0,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        テキストから音声を合成

        Args:
            text: 合成するテキスト
            output_path: 出力ファイルのパス（指定した場合はoutput_dirとoutput_nameは無視）
            output_name: 出力ファイル名（拡張子なし）
            language_code: 言語コード（"ja-JP", "en-US"など）
            voice_name: 音声名（Noneの場合は自動選択）
            voice_gender: 音声の性別
            audio_encoding: オーディオエンコーディング
            speaking_rate: 話速（0.25 - 4.0）
            pitch: ピッチ（-20.0 - 20.0）
            volume_gain_db: 音量（-96.0 - 16.0）
            output_dir: 出力ディレクトリ

        Returns:
            合成結果の辞書
            {
                'audio_file': Path,
                'text': str,
                'language': str,
                'voice_name': str,
                'duration': float (推定),
                'status': 'success' | 'error',
                'error': str (エラー時のみ)
            }
        """
        try:
            print("🎙️ Text-to-Speechで音声合成中...")
            print(f"   Text: {text[:100]}...")
            print(f"   Language: {language_code}")
            print(f"   Speaking Rate: {speaking_rate}")

            # 入力テキストを設定
            synthesis_input = texttospeech.SynthesisInput(text=text)

            # 音声設定
            if voice_name is None:
                # 言語コードから自動選択
                if language_code.startswith("ja"):
                    voice_name = self.JAPANESE_VOICES["female_a"]
                elif language_code.startswith("en"):
                    voice_name = self.ENGLISH_VOICES["female_a"]

            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
                ssml_gender=getattr(texttospeech.SsmlVoiceGender, voice_gender)
            )

            print(f"   Voice: {voice_name}")

            # オーディオ設定
            audio_config = texttospeech.AudioConfig(
                audio_encoding=getattr(texttospeech.AudioEncoding, audio_encoding),
                speaking_rate=speaking_rate,
                pitch=pitch,
                volume_gain_db=volume_gain_db
            )

            # 音声合成を実行
            print("📤 API呼び出し中...")
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )

            print("✓ 音声合成完了")

            # 出力パスを決定
            if output_path is None:
                # 出力ディレクトリの準備
                if output_dir is None:
                    project_root = Path(__file__).parent.parent
                    output_dir = project_root / "data" / "output" / "speech"
                output_dir.mkdir(parents=True, exist_ok=True)

                # 拡張子を決定
                ext_map = {
                    "MP3": ".mp3",
                    "LINEAR16": ".wav",
                    "OGG_OPUS": ".ogg"
                }
                ext = ext_map.get(audio_encoding, ".mp3")

                # ファイル名を生成
                import time
                timestamp = int(time.time())
                filename = f"{output_name}_{timestamp}{ext}"
                output_path = output_dir / filename

            # 音声ファイルを保存
            print(f"💾 音声ファイルを保存中: {output_path}")
            with open(output_path, "wb") as out:
                out.write(response.audio_content)

            print(f"✓ 保存完了: {output_path}")

            # 音声の長さを推定（文字数から）
            estimated_duration = len(text) / 5.0 / speaking_rate  # 日本語は約5文字/秒

            return {
                'audio_file': output_path,
                'text': text,
                'language': language_code,
                'voice_name': voice_name,
                'duration': estimated_duration,
                'status': 'success'
            }

        except Exception as e:
            print(f"❌ エラー: {e}")
            return {
                'audio_file': None,
                'text': text,
                'language': language_code,
                'voice_name': voice_name or "unknown",
                'duration': 0,
                'status': 'error',
                'error': str(e)
            }

    def synthesize_book_narration(
        self,
        book_title: str,
        narration_text: str,
        language: str = "ja",
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        書籍のナレーションを生成

        Args:
            book_title: 書籍タイトル
            narration_text: ナレーション用テキスト
            language: 言語（"ja" or "en"）
            output_dir: 出力ディレクトリ

        Returns:
            合成結果
        """
        # 言語コードを設定
        language_code = "ja-JP" if language == "ja" else "en-US"

        # 出力名を書籍タイトルから生成
        safe_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')[:30]
        output_name = f"{safe_title}_narration"

        # ナレーションに適した設定
        return self.synthesize_speech(
            text=narration_text,
            output_name=output_name,
            language_code=language_code,
            speaking_rate=1.0,  # 標準速度
            pitch=0.0,
            volume_gain_db=0.0,
            output_dir=output_dir
        )

    def list_available_voices(self, language_code: Optional[str] = None) -> List[str]:
        """
        利用可能な音声を一覧表示

        Args:
            language_code: 言語コード（Noneの場合は全て）

        Returns:
            音声名のリスト
        """
        try:
            response = self.client.list_voices(language_code=language_code)
            voices = []

            for voice in response.voices:
                voices.append({
                    'name': voice.name,
                    'languages': voice.language_codes,
                    'gender': texttospeech.SsmlVoiceGender(voice.ssml_gender).name
                })

            return voices

        except Exception as e:
            print(f"❌ エラー: {e}")
            return []


def main():
    """CLI実行用のメイン関数"""
    import argparse

    parser = argparse.ArgumentParser(description='Google Cloud Text-to-Speech クライアント')
    parser.add_argument('text', type=str, help='合成するテキスト')
    parser.add_argument('--output', '-o', type=str, default='speech',
                       help='出力ファイル名（拡張子なし）')
    parser.add_argument('--language', '-l', type=str, default='ja-JP',
                       help='言語コード（ja-JP, en-USなど）')
    parser.add_argument('--voice', '-v', type=str,
                       help='音声名（指定しない場合は自動選択）')
    parser.add_argument('--gender', '-g', type=str, default='NEUTRAL',
                       choices=['NEUTRAL', 'MALE', 'FEMALE'],
                       help='音声の性別')
    parser.add_argument('--speed', '-s', type=float, default=1.0,
                       help='話速（0.25 - 4.0）')
    parser.add_argument('--pitch', '-p', type=float, default=0.0,
                       help='ピッチ（-20.0 - 20.0）')
    parser.add_argument('--volume', type=float, default=0.0,
                       help='音量（-96.0 - 16.0）')
    parser.add_argument('--output-dir', type=str,
                       help='出力ディレクトリ')
    parser.add_argument('--list-voices', action='store_true',
                       help='利用可能な音声を一覧表示')
    parser.add_argument('--credentials', type=str,
                       help='Google Cloud認証情報のパス')

    args = parser.parse_args()

    # クライアントを作成
    client = TextToSpeechClient(credentials_path=args.credentials)

    # 音声一覧表示
    if args.list_voices:
        print("=" * 60)
        print("利用可能な音声")
        print("=" * 60)

        voices = client.list_available_voices(language_code=args.language if args.language else None)

        for voice in voices:
            print(f"\n音声名: {voice['name']}")
            print(f"  言語: {', '.join(voice['languages'])}")
            print(f"  性別: {voice['gender']}")

        print("=" * 60)
        return

    # 出力ディレクトリ
    output_dir = Path(args.output_dir) if args.output_dir else None

    print("=" * 60)
    print("🎙️ Google Cloud Text-to-Speech")
    print("=" * 60)

    # 音声合成
    result = client.synthesize_speech(
        text=args.text,
        output_name=args.output,
        language_code=args.language,
        voice_name=args.voice,
        voice_gender=args.gender,
        speaking_rate=args.speed,
        pitch=args.pitch,
        volume_gain_db=args.volume,
        output_dir=output_dir
    )

    print("\n" + "=" * 60)
    if result['status'] == 'success':
        print("✅ 成功！")
        print(f"📁 出力ファイル: {result['audio_file']}")
        print(f"⏱️  推定長: {result['duration']:.1f}秒")
    else:
        print("❌ 失敗")
        print(f"エラー: {result['error']}")
    print("=" * 60)


if __name__ == '__main__':
    main()
