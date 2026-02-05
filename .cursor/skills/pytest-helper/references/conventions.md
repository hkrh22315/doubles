# pytest の慣習（このプロジェクト）

## 配置

- テストは `tests/` 配下に置く。
- ファイル名: `test_*.py` または `*_test.py`（pytest が自動収集する）。

## 命名

- テスト関数は `test_` で始める。例: `test_get_price_returns_float()`。
- テストクラスは `Test` で始めてもよい。例: `class TestGMOClient:`。

## 構成例

```
tests/
  conftest.py      # 共通フィクスチャ（必要なら）
  test_main.py     # main まわりのテスト
  test_gmo_client.py
  test_risk_manager.py
```

## インポート

- テスト対象はプロジェクトルートを `sys.path` に含めたうえで、`from src.api.gmo_client import GMOClient` のようにインポートする。
- または `python -m pytest` をプロジェクトルートで実行し、`src` をパッケージとして認識させる。
