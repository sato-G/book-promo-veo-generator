# Git運用フロー（Git Flow）

## 概要

本プロジェクトではGit Flow戦略を採用し、**安定性と開発速度の両立**を実現します。

## ブランチ戦略

### 🌟 main（master）ブランチ
- **目的**: プロダクション環境用の安定版
- **原則**: 常に動作する状態を保つ
- **マージ元**: `develop`ブランチのみ
- **保護**: 直接コミット禁止

**運用ルール**:
- ✅ 全てのテストがパスしている
- ✅ コードレビュー完了
- ✅ ドキュメント更新済み
- ✅ CHANGELOGに記載済み

### 🚧 developブランチ
- **目的**: 開発統合ブランチ
- **原則**: 次のリリース候補が集約される
- **マージ元**: `feature/*`ブランチ
- **マージ先**: `main`ブランチ

**運用ルール**:
- ✅ featureブランチからのPR経由でマージ
- ✅ 基本的なテストはパスしている
- ✅ バグ修正もここで統合
- ⚠️ 不安定な実験的機能も許容（ただし明示すること）

### 🔧 feature/*ブランチ
- **目的**: 機能開発・バグ修正
- **命名規則**: `feature/<issue-number>-<short-description>`
  - 例: `feature/123-add-subtitle-animation`
  - 例: `feature/456-fix-tts-timeout`
- **起点**: `develop`ブランチ
- **マージ先**: `develop`ブランチ

**運用ルール**:
- ✅ 1機能 = 1ブランチ（単一責任原則）
- ✅ 小さく作り、早くマージする
- ✅ コミットメッセージは明確に
- ✅ 不要になったブランチは即削除

## 開発フロー

### 1. 新機能開発の開始

```bash
# developブランチを最新化
git checkout develop
git pull origin develop

# featureブランチ作成
git checkout -b feature/123-add-subtitle-animation

# 開発開始
# ...コーディング...

# コミット（Fail-First原則に従う）
git add .
git commit -m "feat: Add subtitle fade-in animation

- Implement fade-in effect for subtitles
- Add animation duration parameter
- Update UI to control animation speed

Refs: #123"
```

### 2. プッシュとPR作成

```bash
# リモートにプッシュ
git push -u origin feature/123-add-subtitle-animation

# GitHub/GitLabでPR作成
# タイトル: [WIP] Add subtitle fade-in animation
# 説明: 機能概要、変更内容、テスト方法を記載
```

### 3. コードレビューと修正

```bash
# レビューコメントに対応
git add .
git commit -m "fix: Address code review comments"

git push
```

### 4. developへのマージ

```bash
# レビュー承認後、PRをマージ
# マージ方法: Squash and Merge（推奨）

# ローカルでブランチ削除
git checkout develop
git pull origin develop
git branch -d feature/123-add-subtitle-animation
```

### 5. mainへのリリース

```bash
# developが十分に安定したらmainへマージ
git checkout main
git pull origin main

# developをマージ（Fast-forward禁止）
git merge --no-ff develop -m "Release v1.2.0

- Add subtitle fade-in animation
- Fix TTS timeout issue
- Improve error handling

See CHANGELOG.md for details"

git push origin main

# タグ作成（セマンティックバージョニング）
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin v1.2.0
```

## コミットメッセージ規約

### フォーマット
```
<type>: <subject>

<body>

<footer>
```

### Type一覧
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント変更のみ
- `style`: コードの意味に影響しない変更（空白、フォーマット等）
- `refactor`: リファクタリング
- `perf`: パフォーマンス改善
- `test`: テスト追加・修正
- `chore`: ビルドプロセス・補助ツールの変更

### 例
```bash
feat: Add video export progress bar

Implement real-time progress tracking for video export process.
- Add progress callback in moviepy_effects.py
- Update Streamlit UI to display progress
- Handle export cancellation gracefully

Refs: #456
```

## 禁止事項（Fail-First原則）

### ❌ 絶対に禁止
1. **mainへの直接コミット**
   - 必ずdevelop経由でマージ

2. **force push（例外なし）**
   ```bash
   # 禁止
   git push --force
   git push --force-with-lease
   ```

3. **エラーの握りつぶしコミット**
   - テスト失敗を無視してコミット
   - try/exceptで例外を隠蔽

4. **大きすぎるPR**
   - 500行以上の変更は分割を検討

5. **未テストコードのマージ**
   - 最低限の動作確認は必須

## ブランチ保護設定（推奨）

### mainブランチ
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators（管理者も例外なし）

### developブランチ
- ✅ Require pull request reviews before merging
- ⚠️ 緊急修正時は管理者のみdirect commit許可

## 緊急修正（Hotfix）

mainで重大なバグが見つかった場合：

```bash
# mainから直接ブランチ作成
git checkout main
git checkout -b hotfix/critical-veo-api-error

# 修正
git add .
git commit -m "fix: Critical Veo API timeout handling"

# mainとdevelopの両方にマージ
git checkout main
git merge --no-ff hotfix/critical-veo-api-error
git push origin main

git checkout develop
git merge --no-ff hotfix/critical-veo-api-error
git push origin develop

# ブランチ削除
git branch -d hotfix/critical-veo-api-error
```

## まとめ

- **main**: 絶対に動く
- **develop**: 次のリリース候補
- **feature**: 機能開発
- **小さく、速く、安全に**開発する
- **Fail-First**: エラーは隠さず、早期に顕在化
