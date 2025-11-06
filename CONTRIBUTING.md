# 貢献ガイド

このプロジェクトへの貢献を歓迎します！以下のガイドラインに従ってください。

## 目次

1. [行動規範](#行動規範)
2. [開発環境のセットアップ](#開発環境のセットアップ)
3. [貢献の流れ](#貢献の流れ)
4. [コーディング規約](#コーディング規約)
5. [Fail-First原則](#fail-first原則)
6. [プルリクエストガイドライン](#プルリクエストガイドライン)
7. [コードレビュー](#コードレビュー)

## 行動規範

- 敬意を持ったコミュニケーション
- 建設的なフィードバック
- 技術的な議論に集中
- 多様な意見を尊重

## 開発環境のセットアップ

詳細は[開発ガイド](docs/development.md)を参照してください。

### クイックスタート

```bash
# リポジトリクローン
git clone <repository-url>
cd book-promo-veo-generator

# 仮想環境作成
python3 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .envにAPIキーを設定

# Google Cloud認証
gcloud auth application-default login
```

## 貢献の流れ

### 1. Issueを確認または作成

既存のIssueを確認し、なければ新規作成：

```markdown
**タイトル**: [Feature] 字幕アニメーション機能の追加

**説明**:
字幕にフェードイン効果を追加したい

**期待される動作**:
- フェードイン時間を指定可能
- 複数の字幕を時間差で表示

**技術的な検討事項**:
- MoviePyのTextClip.fadein()を使用
- パラメータ検証（Fail-First原則）
```

### 2. developブランチから派生

```bash
git checkout develop
git pull origin develop
git checkout -b feature/123-add-subtitle-animation
```

### 3. ドキュメント駆動で開発

**重要**: コードを書く前にドキュメントを書く

#### a. API仕様書を更新

`docs/api-reference.md`に追記：

```markdown
### `add_subtitle_with_animation`

\`\`\`python
def add_subtitle_with_animation(
    video_clip: VideoClip,
    text: str,
    fade_duration: float = 0.5
) -> VideoClip:
    """
    字幕をフェードイン効果付きで追加

    Args:
        video_clip: 対象動画クリップ
        text: 字幕テキスト
        fade_duration: フェードイン時間（秒）

    Raises:
        ValueError: fade_durationが負（Fail-First）
    """
\`\`\`
```

#### b. テストを書く

```python
# tests/test_moviepy_effects.py

def test_add_subtitle_with_animation_normal():
    """正常系: 字幕が追加される"""
    # TODO: 実装

def test_add_subtitle_with_animation_negative_duration():
    """異常系: fade_duration < 0でValueError（Fail-First）"""
    with pytest.raises(ValueError):
        add_subtitle_with_animation(video, "test", fade_duration=-1)
```

#### c. 実装

```python
# generators/moviepy_effects.py

def add_subtitle_with_animation(
    video_clip: VideoClip,
    text: str,
    fade_duration: float = 0.5
) -> VideoClip:
    # Fail-First: 入力検証
    if fade_duration < 0:
        raise ValueError(f"fade_duration must be non-negative, got {fade_duration}")

    # 実装
    txt_clip = TextClip(text, fontsize=70, color='white')
    txt_clip = txt_clip.set_position('center').set_duration(video_clip.duration)
    txt_clip = txt_clip.fadein(fade_duration)

    return CompositeVideoClip([video_clip, txt_clip])
```

### 4. コミット

```bash
git add .
git commit -m "feat: Add subtitle fade-in animation

- Implement fade-in effect for subtitles
- Add fade_duration parameter with validation
- Update API documentation

Refs: #123"
```

### 5. プッシュとPR作成

```bash
git push -u origin feature/123-add-subtitle-animation
```

GitHub/GitLabでPR作成：

**PRテンプレート**:

```markdown
## 概要
字幕にフェードイン効果を追加する機能

## 変更内容
- `add_subtitle_with_animation` 関数を追加
- パラメータ検証（Fail-First原則）
- テストケース追加

## テスト方法
\`\`\`bash
pytest tests/test_moviepy_effects.py::test_add_subtitle_with_animation_normal
\`\`\`

## チェックリスト
- [x] Fail-First原則に従っている
- [x] 型ヒントが付いている
- [x] Docstringが明確
- [x] テストが追加されている
- [x] ドキュメントが更新されている
- [x] 不要なコードが削除されている

## スクリーンショット（該当する場合）
（UIの変更がある場合はスクリーンショットを追加）

Closes #123
```

## コーディング規約

### Python スタイル

- **PEP 8**準拠
- **型ヒント**必須
- **Docstring**（Google形式）必須

```python
def process_video(
    input_path: str,
    output_path: str,
    effects: list[str]
) -> bool:
    """
    動画処理

    Args:
        input_path: 入力動画パス
        output_path: 出力動画パス
        effects: 適用エフェクト一覧

    Returns:
        成功時True

    Raises:
        ValueError: effectsが空の場合（Fail-First）
        FileNotFoundError: input_pathが存在しない
    """
```

### コーディング原則（CLAUDE.md準拠）

1. **DRY (Don't Repeat Yourself)**
   - 重複を避ける
   - 共通処理は関数化

2. **YAGNI (You Aren't Gonna Need It)**
   - 将来必要かもしれない機能は作らない
   - 今必要なものだけ実装

3. **KISS (Keep It Simple, Stupid)**
   - シンプルで明快な実装
   - 複雑さを避ける

4. **Boy Scout Rule**
   - コードを触ったら来た時よりきれいに
   - 不要なコメント・コードを削除

5. **Dead Code Removal**
   - 使われないコードは削除
   - 技術的負債を溜めない

## Fail-First原則

**最重要**: エラーは早期に顕在化させる

### ❌ 禁止事項

```python
# エラーの握りつぶし（絶対禁止）
try:
    result = risky_operation()
except Exception:
    return None  # 失敗を隠蔽

# 未検証の入力を受け入れる
def process(value):
    # valueが不正でも処理を続ける（NG）
    return value * 2
```

### ✅ 推奨事項

```python
# 早期失敗（入力検証）
def process(value: int) -> int:
    if value < 0:
        raise ValueError(f"value must be non-negative, got {value}")

    return value * 2

# エラーは必ず再送出
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise  # 上位に伝播
```

## プルリクエストガイドライン

### PRのサイズ

- **小さく保つ**: 500行以下が理想
- **単一責任**: 1機能 = 1PR
- **早くマージ**: 長期間のブランチは避ける

### PRの説明

- **概要**: 何を変更したか
- **理由**: なぜ変更したか
- **テスト方法**: どうやって確認するか
- **スクリーンショット**: UIの変更がある場合

### レビュー前のチェックリスト

- [ ] Fail-First原則に従っている
- [ ] try/exceptでエラーを握りつぶしていない
- [ ] 型ヒントが適切
- [ ] Docstringが明確
- [ ] テストが追加されている
- [ ] ドキュメントが更新されている
- [ ] 不要なコードが削除されている
- [ ] CLAUDE.mdの原則に従っている

## コードレビュー

### レビュアーの責務

1. **Fail-First原則のチェック**
   - エラーハンドリングは適切か？
   - 入力検証はあるか？

2. **コード品質**
   - YAGNI/DRY/KISSに従っ��いるか？
   - 型ヒント・Docstringはあるか？

3. **テスト**
   - 重要な機能にテストがあるか？
   - エッジケースはカバーされているか？

4. **ドキュメント**
   - API仕様書は更新されているか？

### レビューコメントの例

```markdown
**Good**:
この入力検証は素晴らしいです！Fail-First原則に従っていますね。

**Needs Improvement**:
この`except Exception`はエラーを握りつぶしています。
特定の例外のみキャッチし、再送出してください。

**Suggestion**:
この処理は`moviepy_effects.py`に既存の類似関数があります。
DRY原則に従い、共通化を検討してください。
```

## 質問・サポート

- **Issue**: バグ報告・機能提案
- **Discussions**: 技術的な議論
- **Pull Request**: コードレビュー依頼

貢献ありがとうございます！
