# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- ドキュメント駆動開発の構造
  - `docs/architecture.md`: システムアーキテクチャ設計書
  - `docs/development.md`: 開発ガイド
  - `docs/git-workflow.md`: Git運用フロー
  - `docs/api-reference.md`: API仕様書
- `CONTRIBUTING.md`: 貢献者ガイド
- `CHANGELOG.md`: 変更履歴（本ファイル）

### Changed
- Git戦略をGit Flowに準拠（main/develop/feature）

## [1.0.0] - 2025-11-06

### Added
- 初期リリース: 書籍プロモーション動画生成システム
- Google Veo 3.1による動画生成機能
- Google Cloud TTSによるナレーション生成
- MoviePyによる動画編集機能
  - テキストオーバーレイ
  - フェードイン/アウト効果
- Streamlit UIによるインタラクティブエディター
- Fail-First原則の採用（CLAUDE.md）

### Technical Details
- Python 3.9+対応
- 依存関係: streamlit, moviepy, google-generativeai, google-cloud-texttospeech

---

## 変更履歴の記録方法

### 変更タイプ
- `Added`: 新機能
- `Changed`: 既存機能の変更
- `Deprecated`: 非推奨化（将来削除予定）
- `Removed`: 削除された機能
- `Fixed`: バグ修正
- `Security`: セキュリティ関連の修正

### 記録例

```markdown
## [1.1.0] - 2025-11-10

### Added
- 字幕フェードイン効果機能 (#123)
  - `add_subtitle_with_animation` 関数を追加
  - fade_durationパラメータでアニメーション時間を制御可能

### Fixed
- Veo APIタイムアウト時のエラーハンドリング改善 (#145)
  - TimeoutErrorを明示的にraiseするよう修正（Fail-First原則）

### Changed
- TTS音声の選択肢を拡充 (#156)
  - Neural2音声を追加（より自然な音声）
```

### コミット時のルール

1. **リリース時に更新**
   - developからmainへのマージ時にCHANGELOGを更新

2. **セマンティックバージョニング**
   - MAJOR: 破壊的変更
   - MINOR: 後方互換性のある機能追加
   - PATCH: バグ修正

3. **Issue番号を記載**
   - 各変更にIssue番号を紐付ける

---

[Unreleased]: https://github.com/your-org/book-promo-veo-generator/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-org/book-promo-veo-generator/releases/tag/v1.0.0
