# config と環境変数（このプロジェクト）

## 環境変数

- API キー・シークレットは `.env` で読み込み、コードにハードコードしない。
- `.env.example` をコピーして `.env` を作成し、`GMO_API_KEY` と `GMO_API_SECRET`（またはプロジェクトで定義した変数名）を設定する。
- `.env` は Git にコミットしない（.gitignore に含める）。

## config/config.yaml

- **api**: エンドポイント等。API キー・シークレットは環境変数から読み込む旨をコメントで明示してよい。
- **trading**: 通貨ペア（symbol）、注文タイプ、数量、移動平均の期間・時間足など。
- **risk_management**: 損切り・利確・最大ポジション・反転注文数上限・エラー連続許容回数。
- **execution**: 手動/自動、自動時の間隔（秒）。
- **logging**: ログレベル、ログディレクトリ、取引履歴ディレクトリ。

## 設定の読み込み

- `ConfigLoader`（utils/config_loader.py）で YAML と環境変数を読み込む。API キー・シークレットは専用メソッドで取得し、ログに出力しないこと。
