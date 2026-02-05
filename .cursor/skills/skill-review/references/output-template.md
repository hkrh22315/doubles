# 出力テンプレ（スキルレビュー）

以下のテンプレでレビュー結果を出力する（Markdown）。

## Template

```markdown
## Summary
- 対象: `<skill-path>`
- 結論: （導入可/要修正/要再設計 などを1行で）

## Findings
### Critical
- （該当がなければ「なし」）

### Suggestion
- （該当がなければ「なし」）

### Nice to have
- （該当がなければ「なし」）

## Risks
- **運用**: （例: 発火が曖昧で誤適用の可能性）
- **セキュリティ**: （例: 破壊的操作がガードレールなし）
- **保守性**: （例: 参照構造が複雑で更新が壊れやすい）

## Recommended changes
1. （最優先の修正案。どのファイルのどこをどう変えるか）
2. （次点）

## Quick checklist
- [ ] frontmatter は name/description のみ
- [ ] description は WHAT+WHEN を満たす
- [ ] 参照は1段でリンク切れなし
- [ ] 機密情報/危険操作にガードレールがある
```

## Example（短い例）

```markdown
## Summary
- 対象: `.cursor/skills/example-skill/`
- 結論: 要修正（descriptionが曖昧で誤発火の恐れ）

## Findings
### Critical
- `SKILL.md` の `description` が「手伝う」中心で、WHEN（いつ使う）が不明確。スキルが発火しにくく、別タスクにも誤適用されうる。
  - **なぜ**: descriptionは発火の主要キーで、曖昧だとレビュー/運用時に再現性が落ちるため。
  - **修正案**: WHAT+WHEN とトリガ語（例: 「スキル」「SKILL.md」「.cursor/skills」）を追加して1文にまとめる。

### Suggestion
- `SKILL.md` が長く、詳細説明が混在。`references/` に移し、本文は手順中心に整理すると読みやすい。

### Nice to have
- 出力テンプレを追加して、レビュー結果の形式を固定すると比較しやすい。

## Risks
- **運用**: 発火不全または誤発火で期待通りに適用されない
- **セキュリティ**: なし
- **保守性**: 参照分離がないため更新が破綻しやすい

## Recommended changes
1. `SKILL.md` のdescriptionをWHAT+WHENに修正（トリガ語を追加）
2. 詳細説明を `references/` に移動し、本文を手順中心に整理

## Quick checklist
- [ ] frontmatter は name/description のみ
- [ ] description は WHAT+WHEN を満たす
- [ ] 参照は1段でリンク切れなし
- [ ] 機密情報/危険操作にガードレールがある
```

