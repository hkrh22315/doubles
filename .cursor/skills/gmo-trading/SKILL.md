---
name: gmo-trading
description: GMOコイン API・取引ドメインの仕様と注意点を案内する。GMO API の変更、注文・残高・KLine の実装、config や環境変数の扱いを聞かれたときや、取引所周りのコードを触るときに使用。
---

# GMO 取引スキル

## クイックスタート

1. GMO の API 仕様・制約は [references/api-spec.md](references/api-spec.md) を参照する。
2. このプロジェクトの設定（config.yaml・環境変数）は [references/config-env.md](references/config-env.md) を参照する。
3. コード変更時はレート制限・最小注文単位・エラーハンドリングを満たしているか確認する。

## コードを触るときの確認

- 注文送信・残高取得・KLine 取得など API を呼ぶ処理を変更するときは、[references/api-spec.md](references/api-spec.md) の制約に沿っているか確認する。
- 設定の読み込みや環境変数の扱いを変えるときは、[references/config-env.md](references/config-env.md) と [trading-safety ルール](../../rules/trading-safety.mdc) に従う。
