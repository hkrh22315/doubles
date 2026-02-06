import json
import logging
import os
import re
from typing import Optional

import requests
import discord
from discord import app_commands
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.errors import HttpError

from gdoc_write import append_text as gdoc_append_text


LOGGER = logging.getLogger("discord-memo-bot")


DATE_LINE_RE = re.compile(r"^\d{1,2}/\d{1,2}\s*$")


def _format_http_error_detail(e: HttpError) -> str:
    """
    Google API の HttpError からユーザー向けの詳細メッセージを抽出する。
    秘密情報を含まないよう、error.message と errors[].reason のみを使用する。
    """
    detail = ""
    if getattr(e, "content", None):
        try:
            body = json.loads(e.content.decode("utf-8"))
            err = body.get("error", {})
            if isinstance(err, dict):
                msg = err.get("message", "")
                if msg:
                    detail = msg
                errors = err.get("errors", [])
                if isinstance(errors, list) and errors:
                    reasons = [
                        x.get("reason", "")
                        for x in errors
                        if isinstance(x, dict) and x.get("reason")
                    ]
                    if reasons and not detail:
                        detail = "; ".join(reasons)
                    elif reasons:
                        detail = f"{detail} ({'; '.join(reasons)})"
        except (ValueError, TypeError, UnicodeDecodeError):
            pass
    return detail


def get_latest_memo(raw_text: str) -> Optional[str]:
    """
    ドキュメント全体のテキストから、末尾側にある最新の日付ブロックを抽出する。

    ルール:
    - 日付行は `M/D` または `MM/DD` 形式の 1 行 (例: 2/4, 02/04)。
    - テキスト末尾から上方向に走査し、最初に見つかった日付行を起点として
      その行以降をすべて 1 つのメモとして扱う。
    """
    if not raw_text:
        return None

    lines = raw_text.splitlines()

    # 末尾の空行は無視する
    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        return None

    latest_date_idx = None

    # 下から上に向かって日付行を探す
    for i in range(len(lines) - 1, -1, -1):
        line = lines[i].strip()
        if DATE_LINE_RE.match(line):
            latest_date_idx = i
            break

    if latest_date_idx is None:
        return None

    memo_lines = lines[latest_date_idx:]
    memo_text = "\n".join(memo_lines).strip()
    return memo_text or None


class MemoBot(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        # グローバルスラッシュコマンドを同期
        await self.tree.sync()
        LOGGER.info("Application commands synced.")


def create_export_url(doc_id: str) -> str:
    return f"https://docs.google.com/document/d/{doc_id}/export?format=txt"


def fetch_document_text(doc_id: str, timeout: float = 10.0) -> str:
    url = create_export_url(doc_id)
    LOGGER.debug("Fetching document from %s", url)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def chunk_text(text: str, limit: int = 1900):
    """Discord の 2000 文字制限に余裕を見て分割するジェネレータ。"""
    for i in range(0, len(text), limit):
        yield text[i : i + limit]


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    token = os.getenv("MEMO_BOT_TOKEN")
    doc_id = os.getenv("DOC_ID")

    if not token:
        raise RuntimeError(
            "Environment variable MEMO_BOT_TOKEN is not set. "
            "Set your bot token before running this script."
        )

    if not doc_id:
        raise RuntimeError(
            "Environment variable DOC_ID is not set. "
            "Set your Google Docs document ID before running this script."
        )

    bot = MemoBot()

    @bot.tree.command(name="memo", description="Googleドキュメントの最新メモを送信します。")
    async def memo(interaction: discord.Interaction) -> None:  # type: ignore[override]
        await interaction.response.defer(thinking=True)

        try:
            text = fetch_document_text(doc_id)
        except requests.HTTPError as e:
            LOGGER.exception("Failed to fetch document: HTTP error")
            await interaction.followup.send(
                f"Googleドキュメントの取得に失敗しました (HTTP error: {e.response.status_code}).",
                ephemeral=True,
            )
            return
        except requests.RequestException as e:
            LOGGER.exception("Failed to fetch document: request error")
            await interaction.followup.send(
                f"Googleドキュメントの取得中にエラーが発生しました: {e}",
                ephemeral=True,
            )
            return

        memo_text = get_latest_memo(text)

        if not memo_text:
            await interaction.followup.send(
                "日付行を含む最新メモが見つかりませんでした。"
                "Googleドキュメントの形式を確認してください。",
                ephemeral=True,
            )
            return

        header = "**最新のメモ**"

        # 短い場合は 1 メッセージで送信
        if len(memo_text) <= 1900:
            await interaction.followup.send(f"{header}\n{memo_text}")
            return

        # 長い場合は分割送信
        await interaction.followup.send(header)
        for chunk in chunk_text(memo_text):
            await interaction.channel.send(chunk)  # type: ignore[arg-type]

    @bot.tree.command(
        name="send_memo",
        description="メモを Google ドキュメントの末尾に送信します。",
    )
    @app_commands.describe(content="メモの本文")
    async def send_memo(
        interaction: discord.Interaction, content: app_commands.Range[str, 1, 3000]
    ) -> None:
        await interaction.response.defer(thinking=True, ephemeral=True)

        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            await interaction.followup.send(
                "Google ドキュメントへの書き込みは設定されていません。"
                "GOOGLE_APPLICATION_CREDENTIALS を設定してください。",
                ephemeral=True,
            )
            return

        try:
            gdoc_append_text(doc_id, content)
        except DefaultCredentialsError as e:
            LOGGER.exception("Google 認証エラー")
            await interaction.followup.send(
                f"Google ドキュメントへの書き込みに必要な認証がありません: {e}",
                ephemeral=True,
            )
            return
        except HttpError as e:
            LOGGER.exception("Google Docs API エラー")
            status = e.resp.status if e.resp else "?"
            msg = (
                f"Google ドキュメントの更新に失敗しました (HTTP {status})。"
                "ドキュメントがサービスアカウントと共有されているか確認してください。"
            )
            detail = _format_http_error_detail(e)
            if detail:
                msg = f"{msg}\n詳細: {detail}"
            await interaction.followup.send(msg, ephemeral=True)
            return
        except OSError as e:
            LOGGER.exception("Google 認証ファイルの読み込みエラー")
            await interaction.followup.send(
                f"認証ファイルの読み込みに失敗しました: {e}",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            "Google ドキュメントに送信しました。",
            ephemeral=True,
        )

    LOGGER.info("Starting MemoBot...")
    bot.run(token)


if __name__ == "__main__":
    main()

