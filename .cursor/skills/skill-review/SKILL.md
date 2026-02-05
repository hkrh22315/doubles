---
name: skill-review
description: Cursorスキル（.cursor/skills/**/SKILL.md と付随 references/scripts）の品質・発火条件・保守性・セキュリティ・リポジトリ運用整合性をレビューし、Critical/Suggestion/Nice to have の指摘と具体的改善案をテンプレ形式で出力する。ユーザーが「スキルをレビュー」「SKILL.mdを見て」「スキルを追加/更新したい」「このスキル大丈夫？」などと言ったとき、またはスキルディレクトリの変更点レビュー時に使用。
---

# スキルレビュー（Cursor Skill Review）

## クイックスタート

1. レビュー対象のスキルディレクトリ（例: `.cursor/skills/<skill-name>/`）を特定する
2. 変更点がある場合は差分（git diff / 変更ファイル）を最優先で読む
3. `SKILL.md` と、参照されている `references/`・`scripts/` を必要に応じて読む
4. チェックリストに沿って指摘を分類し、テンプレでレビュー結果を出力する

## レビュー手順

### 0) 入力を揃える（不足している場合は確認）

- 対象のスキルパス（ディレクトリ）
- 目的（どんなタスクで使うスキルか）
- 変更点（新規作成 / 更新、diffの有無）
- 付随ファイル（`references/`、`scripts/`、`assets/` があれば）

### 1) まず `SKILL.md` を最初に読む

- frontmatter の `name` / `description` が仕様通りか
- description が **WHAT（何をする）+ WHEN（いつ使う）** を含み、発火しやすいか
- 本文が「実行可能な手順」になっているか（曖昧な丸投げがないか）

### 2) 参照ファイルを辿って整合性を確認する

- `SKILL.md` から参照されている `references/*.md` は **1段で辿れる**か（深いネストを避ける）
- リンク切れや、参照の前提が崩れていないか

### 3) リポジトリ運用への整合性を確認する

スキルがリポジトリ内のルールや運用に影響する場合、次も確認する:

- `.cursorrules` や `.cursor/rules/*.mdc` と矛盾する推奨をしていないか
- 既存スキル（例: `.cursor/skills/code-review/`、`.cursor/skills/skill-creator/`）と重複・衝突していないか
- OS/シェル前提（例: Windows/PowerShell）を暗黙に固定していないか（必要なら明示する）

### 4) セキュリティと安全性（特に重要）

- シークレット/APIキー/個人情報をスキルに含めない（ログ出力例にも含めない）
- 破壊的な操作（削除、強制上書き、強制push等）を促す場合は、強いガードレールを入れる
- ツール実行を伴う場合は、前提・影響・失敗時の扱いを明確にする

## チェックリストと出力テンプレ

- 詳細チェックリスト: [references/checklist.md](references/checklist.md)
- 出力テンプレ: [references/output-template.md](references/output-template.md)

## 任意の自動検証（このリポジトリにある場合）

リポジトリに `.cursor/skills/skill-creator/` が存在する場合、スキルの形式チェックに次を使える:

- 形式の簡易検証（例）: `python .cursor/skills/skill-creator/scripts/quick_validate.py .cursor/skills/<skill-name>`
- パッケージング（例）: `python .cursor/skills/skill-creator/scripts/package_skill.py .cursor/skills/<skill-name>`

## フィードバックの重要度（Severity）

- **Critical**: マージ/導入前に必ず直すべき問題（安全性・機密・破壊的操作・発火不全・明確な誤り）
- **Suggestion**: 品質や保守性を上げる改善提案（読みやすさ、網羅性、手順の明確化）
- **Nice to have**: 任意の改善（例追加、表現の統一、軽微な整理）

## レビュー出力ルール

- 指摘は必ず「どこ（ファイル/節）」「何が問題か」「なぜ問題か」「どう直すか」をセットで書く
- 可能なら、修正案は **差分が想像できるレベル**の具体性で書く
- 不確実な場合は「前提」を明示して、確認すべき事項を短く列挙する

