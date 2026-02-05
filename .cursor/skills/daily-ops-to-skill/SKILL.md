---
name: daily-ops-to-skill
description: 一日に二回以上行う操作をスキル化する判断と手順を案内する。ユーザーが「繰り返し操作をスキルにしたい」「一日二回以上やる操作をスキルにする」「スキルを作りたい」「スキルを改善したい」と言ったとき、または頻出操作の整理を依頼したときに使用する。create skill, improve skill, daily operations にも対応。
---

# 一日に二回以上やる操作はスキルにする

## 概要

「一日に二回以上やる操作はスキルにする」は、繰り返し作業を Cursor スキルにまとめる方針である。このスキルは、頻出操作の洗い出し、スキル化の判断、および新規スキル作成・既存スキル改善の手順を一貫して案内する。

## 頻出操作の洗い出し

1. ユーザーに「一日に二回以上やっている操作」を挙げてもらう。会話の文脈から既に挙がっている場合はそれを利用する。
2. 操作ごとに次の点を確認する: 何をするか、いつ行うか、手順は言語化できるか。
3. リストが空の場合は、「今日やった繰り返し作業」「毎日同じようにしている手順」を短く聞く。

## スキル化の判断

次のいずれかに当てはまる操作はスキル化の候補とする。

- 一日に二回以上、または週に複数回同じ手順を行っている
- 手順が数ステップ以上あり、説明すれば再現できる
- 同じコマンド・同じファイル編集・同じチェックリストを繰り返している
- スキルにすると「発話だけで同じ結果を出せる」ようになる

逆に、一度きり・文脈に強く依存する・手順が曖昧なものは、まずは手順を固めてからスキル化を検討する。

## 作成・改善の流れ

### 新規スキルを作る場合

1. プロジェクト内スキルなら `.cursor/skills/<skill-name>/`、個人用なら `~/.cursor/skills/<skill-name>/` を想定する。
2. ひな形生成: プロジェクトルートで `python .cursor/skills/skill-creator/scripts/init_skill.py <skill-name> --path .cursor/skills` を実行する（個人用の場合は `--path` を適宜変更）。
3. [skill-creator](.cursor/skills/skill-creator/) の SKILL.md に従い、frontmatter の `description`（WHAT + WHEN、発火キーワード）と本文の手順を書く。
4. Cursor 組み込みの create-skill を使う場合は、スキル構造・description の書き方・ベストプラクティスを案内してもらうとよい。

### 既存スキルを改善する場合

1. [skill-review](.cursor/skills/skill-review/) を適用する。
2. チェックリストと出力テンプレに沿ってレビューし、Critical / Suggestion / Nice to have の指摘を得る。
3. Critical があれば修正案に従って修正し、必要に応じて Suggestion も反映する。

## リソース

- 新規スキルの作成・構造: [.cursor/skills/skill-creator/](.cursor/skills/skill-creator/)
- 既存スキルのレビュー・改善: [.cursor/skills/skill-review/](.cursor/skills/skill-review/)
