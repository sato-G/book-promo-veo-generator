# 📚 Book Promo Video Generator (Veo 3.1 Edition)

書籍プロモーション動画を自動生成するシステム

## 🎯 主な機能

### 1. AI動画生成（Veo 3.1）
- Google Veo 3.1を使って静止画から動画を生成
- 人物の動き、カメラワークを自動で追加
- ドラマチックな演出

### 2. ナレーション生成
- Google Cloud Text-to-Speech API
- 日本語ナレーション対応
- 男性/女性の声を選択可能

### 3. インタラクティブエディター
- Streamlit UIで簡単編集
- 本の表紙・タイトルをオーバーレイ
- リアルタイムプレビュー

## 🚀 使い方

### インストール

```bash
# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
```

### 認証設定

```bash
# Google Cloud認証
gcloud auth application-default login

# APIキーを.envに設定
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### UI起動

```bash
streamlit run ui/video_editor.py
```

## 📁 プロジェクト構造

```
book-promo-veo-generator/
├── ui/                          # Streamlit UI
│   └── video_editor.py         # メインエディター
├── generators/                  # 動画生成スクリプト
│   ├── veo_generator.py        # Veo 3.1動画生成
│   ├── moviepy_effects.py      # MoviePy効果
│   └── tts_client.py           # TTS（音声合成）
├── data/                        # 素材データ
│   ├── books/                  # 書籍素材
│   └── output/                 # 生成済み動画
├── requirements.txt             # 依存関係
├── .env.example                 # 環境変数テンプレート
└── README.md                    # このファイル
```

## 🎬 動画生成例

### 「あの戦争は何だったのか」
- Veo 3.1で兵士の行進シーンを動画化
- 重厚な男性ナレーション
- 「続きは本書で」字幕

### 「腸と脳」の科学
- 表紙のズームイン効果
- 科学的で知的な女性ナレーション
- 「答えは本書で」字幕

## 🔧 技術スタック

- **動画生成:** Google Veo 3.1 API
- **動画編集:** MoviePy
- **音声合成:** Google Cloud Text-to-Speech
- **UI:** Streamlit
- **画像処理:** Pillow

## 📝 ライセンス

MIT License

## 🙏 謝辞

Google Veo 3.1, Google Cloud TTS APIを使用しています。
