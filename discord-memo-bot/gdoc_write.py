"""
Google Docs API を用いて、指定ドキュメントの末尾にメモを追記するモジュール。

サービスアカウント認証を使用する。環境変数 GOOGLE_APPLICATION_CREDENTIALS に
JSON キーファイルの絶対パスを設定すること。
"""

import logging
import os
from datetime import datetime
from typing import Optional

from google.auth.exceptions import DefaultCredentialsError
from google.oauth2 import service_account
from googleapiclient.discovery import build

LOGGER = logging.getLogger("discord-memo-bot")

# Google Docs API のスコープ（ドキュメントの閲覧・編集）
SCOPES = ["https://www.googleapis.com/auth/documents"]


def _get_docs_service():
    """サービスアカウントで Google Docs API クライアントを構築する。"""
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not os.path.isfile(creds_path):
        raise DefaultCredentialsError(
            "GOOGLE_APPLICATION_CREDENTIALS が未設定か、指定パスにファイルがありません。"
        )
    credentials = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES
    )
    return build("docs", "v1", credentials=credentials)


def _document_end_index(service, doc_id: str) -> int:
    """
    ドキュメントの末尾のインデックス（挿入位置）を取得する。
    body.content の最後の要素の endIndex を使用する。
    """
    doc = service.documents().get(documentId=doc_id).execute()
    body = doc.get("body", {})
    content = body.get("content", [])
    if not content:
        return 1
    return content[-1].get("endIndex", 1)


def append_text(doc_id: str, body_text: str, date_line: Optional[str] = None) -> None:
    """
    指定 Google ドキュメントの末尾に、日付行＋空行＋本文を追記する。

    既存のメモ形式（日付行 M/D + 本文）に合わせ、先頭に今日の日付行を付与する。
    date_line を渡した場合はそれを使用し、None の場合は今日の M/D を使用する。

    Args:
        doc_id: Google ドキュメント ID
        body_text: メモ本文（ユーザー入力）
        date_line: 先頭に付ける日付行（例: "2/6"）。None の場合は今日の日付

    Raises:
        DefaultCredentialsError: 認証情報が未設定または無効な場合
        HttpError: Google Docs API の HTTP エラー
    """
    if date_line is None:
        now = datetime.now()
        date_line = f"{now.month}/{now.day}"

    # 追記するテキスト: 日付行 + 空行 + 本文 + 末尾改行
    text_to_insert = f"{date_line}\n\n{body_text.rstrip()}\n"

    service = _get_docs_service()
    end_index = _document_end_index(service, doc_id)

    # 末尾に追記するため、body の最後の endIndex を挿入位置に使う
    requests = [
        {
            "insertText": {
                "location": {"index": end_index},
                "text": text_to_insert,
            }
        }
    ]
    service.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": requests},
    ).execute()
    LOGGER.info("Appended memo to document %s (date line: %s)", doc_id, date_line)
