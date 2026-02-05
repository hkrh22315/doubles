---
name: pytest-helper
description: pytest でテストを書く・足す・実行する手順を案内する。テスト追加・修正、pytest の実行オプション、カバレッジの見方を聞かれたときや、テストを書いてほしいと言ったときに使用。
---

# pytest ヘルパー

## クイックスタート

1. テストを書く／足すときは、プロジェクトの `tests/` 構成に合わせる（[references/conventions.md](references/conventions.md)）。
2. テスト実行はプロジェクトルートで `pytest` または `python -m pytest` を使う。
3. オプションやカバレッジは [references/run-options.md](references/run-options.md) を参照。

## テストを書く／足すとき

- 新規テストファイルは `tests/` 配下に `test_*.py` または `*_test.py` で作成する。
- 既存モジュールに対応するテストは、`tests/test_<module>.py` のように対応関係が分かる名前にする。
- フィクスチャや共通 setup は `conftest.py` にまとめてよい。
- テスト追加・修正後は [testing ルール](../../rules/testing.mdc) に従い、完了前に pytest を実行する。

## 実行とカバレッジ

- 詳細な実行オプションとカバレッジの見方: [references/run-options.md](references/run-options.md)。
