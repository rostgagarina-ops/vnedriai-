import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "leads.db"


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                source TEXT,
                created_at TEXT NOT NULL,
                brief_json TEXT
            )
            """
        )


def upsert_lead(user_id: int, username: str | None, full_name: str, source: str) -> None:
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO leads (user_id, username, full_name, source, created_at, brief_json)
            VALUES (?, ?, ?, ?, ?, NULL)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name,
                source = COALESCE(leads.source, excluded.source)
            """,
            (user_id, username, full_name, source, now),
        )


def save_brief(user_id: int, brief: dict) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE leads SET brief_json = ? WHERE user_id = ?",
            (json.dumps(brief, ensure_ascii=False), user_id),
        )
