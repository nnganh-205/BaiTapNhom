import os
import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.getenv("CHATBOT_SQLITE_DB_PATH", os.path.join(BASE_DIR, "chat_history.db"))


@contextmanager
def _get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    with _get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_sessions (
                user_id TEXT NOT NULL,
                chat_session_id TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, chat_session_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                chat_session_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id, chat_session_id)
                    REFERENCES chat_sessions(user_id, chat_session_id)
                    ON DELETE CASCADE
            )
            """
        )


def save_thread(user_id: str, chat_session_id: str) -> None:
    with _get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO users(user_id) VALUES (?)", (user_id,))
        conn.execute(
            "INSERT OR IGNORE INTO chat_sessions(user_id, chat_session_id) VALUES (?, ?)",
            (user_id, chat_session_id),
        )


def get_user_threads(user_id: str) -> List[Dict[str, str]]:
    """Get all chat sessions for a user ordered by recent access."""
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT chat_session_id, created_at, updated_at, is_active
            FROM chat_sessions
            WHERE user_id = ?
            ORDER BY updated_at DESC
            """,
            (user_id,),
        ).fetchall()

    return [dict(row) for row in rows]


def update_thread_access(user_id: str, chat_session_id: str, is_active: Optional[bool] = None) -> None:
    with _get_connection() as conn:
        if is_active is None:
            conn.execute(
                """
                UPDATE chat_sessions
                SET updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND chat_session_id = ?
                """,
                (user_id, chat_session_id),
            )
        else:
            conn.execute(
                """
                UPDATE chat_sessions
                SET is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND chat_session_id = ?
                """,
                (1 if is_active else 0, user_id, chat_session_id),
            )


def save_message(user_id: str, chat_session_id: str, role: str, content: str) -> None:
    if role not in {"user", "assistant", "system"}:
        raise ValueError("role must be one of: user, assistant, system")

    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO messages(user_id, chat_session_id, role, content)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, chat_session_id, role, content),
        )


def get_thread_messages(user_id: str, chat_session_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
    query = (
        """
        SELECT role, content, created_at
        FROM messages
        WHERE user_id = ? AND chat_session_id = ?
        ORDER BY id DESC
        """
    )
    params = [user_id, chat_session_id]

    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    with _get_connection() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()

    data = [dict(row) for row in rows]
    data.reverse()
    return data

