## 概要

このプロジェクトは、単一の Google ドキュメントに書かれたメモのうち、
**一番下にある日付行から末尾までのブロック**を Discord の `/memo` コマンドで
取得して送信する Python 製ボットです。

AWS EC2(Ubuntu) 上で常時稼働させることを想定しています。

---

## Google ドキュメントの準備

- メモ用 Google ドキュメントを 1 つ用意します。
- 共有設定を **「リンクを知っている全員が閲覧可（閲覧のみ）」** に変更します。
- URL からドキュメント ID をメモしておきます。  
  例: `https://docs.google.com/document/d/THIS_IS_DOC_ID/edit`  
  → `THIS_IS_DOC_ID` がドキュメント ID です。

### メモの書き方ルール

ボットが正しく最新メモを抽出できるよう、以下のルールを守ってください。

- 日付行は `M/D` または `MM/DD` 形式で 1 行だけに書く。
  - 例: `2/4`、`02/04` など。
- 日付行の直後の行から、その日付に対応するメモ本文を書く。
- 別の日付のメモを書くときは、1 行以上の空行を挟んでから次の日付行を書く。

抽出の挙動:

- ドキュメントの一番下の行から上方向へ走査し、
  **最初に見つかった日付行から末尾まで**を「最新のメモ」として扱います。

### Google ドキュメントへの書き込み（`/send_memo` を使う場合）

`/send_memo` でメモをドキュメントの末尾に追記するには、**Google Docs API** と**サービスアカウント**の設定が必要です。

1. **Google Cloud** でプロジェクトを作成し、**Google Docs API** を有効化します。
2. **サービスアカウント**を作成し、JSON キーをダウンロードします。
3. メモ用の Google ドキュメントを、そのサービスアカウントのメール  
   （`xxx@xxx.iam.gserviceaccount.com`）と **編集者** で共有します。
4. サーバー（または実行環境）に JSON キーファイルを配置し、環境変数  
   `GOOGLE_APPLICATION_CREDENTIALS` にその**絶対パス**を設定します。  
   例: systemd の `Environment=GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json` に追加。

**注意**: サービスアカウントの JSON キーは秘密情報です。`.gitignore` に含め、**リポジトリにコミットしない**でください。`GOOGLE_APPLICATION_CREDENTIALS` が未設定の場合は `/send_memo` のみ利用できず、`/memo`（読み取り）は従来どおり動作します。

---

## Discord アプリケーションと Bot の作成

1. ブラウザで Discord Developer Portal を開き、  
   「New Application」から新しいアプリケーションを作成します。
2. 左側メニューの「Bot」タブで **Add Bot** を押して Bot ユーザーを追加します。
3. Bot トークンを発行し、後で環境変数 `MEMO_BOT_TOKEN` に設定できるよう控えておきます。
   （`bot.py` が参照するのは `MEMO_BOT_TOKEN` です。）
4. 「OAuth2 → URL Generator」で下記を選択して招待 URL を生成します。
   - **SCOPES**: `bot`, `applications.commands`
   - **BOT PERMISSIONS**: 少なくとも `Send Messages`
5. 生成された URL を開き、Bot を自分の Discord サーバーに招待します。

---

## 必要な環境 / ライブラリ

- Python 3.10+ 推奨
- ライブラリ:
  - `discord.py` (v2 系)
  - `requests`
  - `google-api-python-client`, `google-auth`（Google ドキュメントへの書き込みを行う場合）

ローカル、または EC2 上で以下を実行してインストールします。

```bash
pip install -r requirements.txt
```

---

## `bot.py` の動作概要

- 起動時に環境変数から設定を読み込みます。
  - `MEMO_BOT_TOKEN`: Discord Bot のトークン
  - `DOC_ID`: メモを格納している Google ドキュメントの ID
- `https://docs.google.com/document/d/{DOC_ID}/export?format=txt` から
  プレーンテキストを取得します。
- 正規表現 `^\d{1,2}/\d{1,2}\s*$` にマッチする行を「日付行」と見なし、
  テキスト末尾から上方向に探索します。
- 一番下側にある日付行が見つかったら、その行以降をすべて
  「最新メモ」として抽出します。
- Discord のスラッシュコマンドで次の処理を呼び出せます。
  - **`/memo`**: 上記の処理を実行し、抽出したメモを 2000 文字制限に合わせて 1〜複数メッセージに分割して送信します。
  - **`/send_memo`**: 引数で渡したメモ本文を、今日の日付行（`M/D`）を付与して Google ドキュメントの末尾に追記します。書き込みには Google Docs API とサービスアカウント認証が必要です（下記「Google ドキュメントへの書き込み」を参照）。

---

## AWS EC2 上でのセットアップ手順 (Ubuntu 例)

### 1. EC2 インスタンス作成

1. AWS コンソールで EC2 を開き、「インスタンスを起動」から Ubuntu ベースの AMI を選択します。
2. インスタンスタイプは `t3.micro` など小さなもので十分です。
3. セキュリティグループで
   - インバウンド: `SSH (22)` を自分の IP のみに許可
   を設定します。
4. キーペアを作成してダウンロードし、そのキーファイルで SSH 接続します。

### 2. Python 環境とコード配置

```bash
ssh -i your-key.pem ubuntu@EC2_PUBLIC_IP

sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip git

mkdir -p ~/discord-memo-bot
cd ~/discord-memo-bot
```

このリポジトリ内のファイル（`bot.py`、`requirements.txt` など）を
`~/discord-memo-bot` に配置します。

ライブラリをインストールします。

```bash
pip3 install --user -r requirements.txt
```

### 3. 環境変数の設定

EC2 では `~/.bashrc` に以下を追記し、ログイン時に環境変数が読み込まれるようにします。

```bash
export MEMO_BOT_TOKEN="あなたのBotトークン"
export DOC_ID="あなたのGoogleドキュメントID"
# /send_memo で書き込みする場合（JSON キーの絶対パスを指定）
export GOOGLE_APPLICATION_CREDENTIALS="/home/ubuntu/discord-memo-bot/あなたのキーファイル名.json"
```

パスは実際に配置した JSON の絶対パスに合わせてください。設定を反映するには次を実行します。

```bash
source ~/.bashrc
```

### 4. 手動起動での動作確認

```bash
cd ~/discord-memo-bot
python3 bot.py
```

Bot がオンラインになったら、招待済みサーバーの任意のチャンネルで
`/memo` と入力し、最新の日付ブロックが送信されることを確認します。

---

## systemd による常時起動

EC2 上で Bot を 24 時間稼働させるために、`systemd` サービスとして登録します。

### サービスファイルの例

以下は `/etc/systemd/system/discord-memo-bot.service` に配置する例です。

```ini
[Unit]
Description=Discord Memo Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/discord-memo-bot
ExecStart=/usr/bin/python3 /home/ubuntu/discord-memo-bot/bot.py
Restart=always
Environment=MEMO_BOT_TOKEN=your_discord_bot_token
Environment=DOC_ID=your_google_document_id
# /send_memo で書き込みする場合のみ:
# Environment=GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

[Install]
WantedBy=multi-user.target
```

`User` や `WorkingDirectory` のパスは実際の環境に合わせて変更してください。

### 有効化と起動

```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-memo-bot
sudo systemctl start discord-memo-bot
sudo systemctl status discord-memo-bot
```

`active (running)` になっていれば、サーバー再起動後も自動で Bot が起動します。

---

## トラブルシューティングのヒント

- `/memo` を実行しても何も返らない場合:
  - Google ドキュメントの共有設定が「リンクを知っている全員が閲覧可」になっているか確認。
  - ドキュメント内に `M/D` or `MM/DD` 形式の日付行が 1 行だけで書かれているか確認。
- systemd で起動しない場合:
  - `sudo journalctl -u discord-memo-bot -e` でログを確認。
  - `Environment` のトークンや DOC_ID が正しいか確認。

