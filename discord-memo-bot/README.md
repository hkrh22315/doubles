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

---

## Discord アプリケーションと Bot の作成

1. ブラウザで Discord Developer Portal を開き、  
   「New Application」から新しいアプリケーションを作成します。
2. 左側メニューの「Bot」タブで **Add Bot** を押して Bot ユーザーを追加します。
3. Bot トークンを発行し、後で環境変数 `DISCORD_TOKEN` に設定できるよう控えておきます。
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

ローカル、または EC2 上で以下を実行してインストールします。

```bash
pip install -r requirements.txt
```

---

## `bot.py` の動作概要

- 起動時に環境変数から設定を読み込みます。
  - `DISCORD_TOKEN`: Discord Bot のトークン
  - `DOC_ID`: メモを格納している Google ドキュメントの ID
- `https://docs.google.com/document/d/{DOC_ID}/export?format=txt` から
  プレーンテキストを取得します。
- 正規表現 `^\d{1,2}/\d{1,2}\s*$` にマッチする行を「日付行」と見なし、
  テキスト末尾から上方向に探索します。
- 一番下側にある日付行が見つかったら、その行以降をすべて
  「最新メモ」として抽出します。
- Discord のスラッシュコマンド `/memo` でこの処理を呼び出し、
  抽出したメモを 2000 文字制限に合わせて 1〜複数メッセージに分割して送信します。

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

`~/.bashrc` などに以下を追記します。

```bash
export DISCORD_TOKEN="あなたのBotトークン"
export DOC_ID="あなたのGoogleドキュメントID"
```

設定を反映します。

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
Environment=DISCORD_TOKEN=your_discord_bot_token
Environment=DOC_ID=your_google_document_id

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

