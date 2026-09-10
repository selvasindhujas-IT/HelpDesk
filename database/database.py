"""
database/database.py
-----------------------
SQLite persistence layer for chat history and user feedback.

Stores: session id, user question, AI response, timestamp, problem
category, and feedback (helpful / not helpful / none yet).
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
from contextlib import contextmanager

from config.config import Config


@contextmanager
def get_connection():
    """Yield a SQLite connection, ensuring it is always closed properly."""
    conn = sqlite3.connect(Config.SQLITE_DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_database() -> None:
    """Create the chat_history table if it does not already exist."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_question TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                category TEXT,
                sources TEXT,
                feedback TEXT DEFAULT 'none',
                timestamp TEXT NOT NULL
            )
            """
        )


def insert_chat_record(
    session_id: str,
    user_question: str,
    ai_response: str,
    category: Optional[str] = None,
    sources: Optional[str] = None,
) -> int:
    """Insert a new chat record and return its row id."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO chat_history
                (session_id, user_question, ai_response, category, sources, feedback, timestamp)
            VALUES (?, ?, ?, ?, ?, 'none', ?)
            """,
            (
                session_id,
                user_question,
                ai_response,
                category or "general",
                sources or "",
                datetime.now().isoformat(),
            ),
        )
        return cursor.lastrowid


def update_feedback(record_id: int, feedback: str) -> bool:
    """Update the feedback field ('helpful' or 'not_helpful') for a record."""
    try:
        with get_connection() as conn:
            conn.execute(
                "UPDATE chat_history SET feedback = ? WHERE id = ?",
                (feedback, record_id),
            )
        return True
    except Exception:
        return False


def get_all_chat_history(limit: int = 200) -> List[Dict]:
    """Return chat history records, most recent first."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM chat_history ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_statistics() -> Dict:
    """Compute simple aggregate statistics for the Statistics page."""
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM chat_history").fetchone()["c"]
        helpful = conn.execute(
            "SELECT COUNT(*) AS c FROM chat_history WHERE feedback = 'helpful'"
        ).fetchone()["c"]
        not_helpful = conn.execute(
            "SELECT COUNT(*) AS c FROM chat_history WHERE feedback = 'not_helpful'"
        ).fetchone()["c"]
        category_rows = conn.execute(
            """
            SELECT category, COUNT(*) AS count
            FROM chat_history
            GROUP BY category
            ORDER BY count DESC
            """
        ).fetchall()

    return {
        "total_queries": total,
        "helpful_responses": helpful,
        "not_helpful_responses": not_helpful,
        "no_feedback_yet": total - helpful - not_helpful,
        "category_breakdown": [dict(row) for row in category_rows],
        "most_common_category": category_rows[0]["category"] if category_rows else "N/A",
    }
