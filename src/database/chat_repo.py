"""
SQLite persistence for assistant chat conversations.

Conversations are scoped per user so that the Streamlit widget can restore
the conversation after a page rerun (Streamlit re-renders the page, and the
browser widget reloads). The table is created inside ``init_db`` so the
schema is guaranteed to exist before any request is served.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional

from src.database.db import DB_PATH, get_conn

CHAT_LIMIT_DEFAULT = 50


def init_chat_table(db_path: str = DB_PATH) -> None:
    """Create the ChatMessages table if it does not exist."""
    conn = get_conn(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ChatMessages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            page TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def add_chat_message(
    user_id: int,
    role: str,
    content: str,
    page: str = "",
    db_path: str = DB_PATH,
) -> int:
    """Insert a single chat message and return its row id."""
    conn = get_conn(db_path)
    created_at = datetime.utcnow().isoformat()
    cur = conn.execute(
        """
        INSERT INTO ChatMessages (user_id, created_at, role, content, page)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, created_at, role, content, page or None),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return int(row_id)


def get_chat_history(
    user_id: int,
    limit: int = CHAT_LIMIT_DEFAULT,
    db_path: str = DB_PATH,
) -> List[Dict[str, Any]]:
    """Return the most recent chat messages for a user, oldest first."""
    conn = get_conn(db_path)
    rows = conn.execute(
        """
        SELECT role, content, created_at, page
        FROM ChatMessages
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def clear_chat_history(user_id: int, db_path: str = DB_PATH) -> None:
    """Remove every chat message belonging to a user."""
    conn = get_conn(db_path)
    conn.execute("DELETE FROM ChatMessages WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_chat_history_pairs(
    user_id: int,
    limit: int = CHAT_LIMIT_DEFAULT,
    db_path: str = DB_PATH,
) -> List[Dict[str, str]]:
    """Return chat history as OpenAI-style ``{"role", "content"}`` pairs."""
    rows = get_chat_history(user_id, limit=limit, db_path=db_path)
    return [{"role": r["role"], "content": r["content"]} for r in rows]
