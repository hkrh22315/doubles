# pytest の実行オプションとカバレッジ

## 基本的な実行

```bash
# プロジェクトルートで
pytest
# または
python -m pytest
```

## よく使うオプション

| オプション | 説明 |
|------------|------|
| `-v` | 詳細表示（テスト名を表示） |
| `-q` | 簡潔表示 |
| `-x` | 最初の失敗で停止 |
| `-k "キーワード"` | 名前がキーワードにマッチするテストのみ実行 |
| `--lf` | 前回失敗したテストのみ再実行 |
| `--ff` | 前回失敗したテストを先に実行 |
| `tests/path/` | 特定ディレクトリのみ実行 |

例:

```bash
pytest -v -x
pytest -k "gmo"
pytest tests/
```

## カバレッジ

```bash
# pytest-cov が入っている場合
pytest --cov=src --cov-report=term-missing
```

- `--cov=src`: カバレッジ対象を `src` パッケージに限定。
- `--cov-report=term-missing`: ターミナルに未カバー行を表示。
- `--cov-report=html`: `htmlcov/` に HTML レポートを出力。

カバレッジの解釈:

- 行カバレッジが 0% のファイルは、そのテスト実行では一度も実行されていない。
- `term-missing` で表示される行番号は、テストで通っていない行の目安。
