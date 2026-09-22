"""
Лёгкое хранилище на SQLite (встроено в Python, ставить ничего не нужно).

Две таблицы:
  - messages — история переписки по сессиям (нужна агенту для контекста).
  - items    — универсальная таблица "что угодно": заметки, идеи, сгенерированный
               контент и т.п. Формат — (тип, JSON с данными, дата). 
               
Если для кейса понадобится более сложная схема (несколько связанных таблиц) —
это нормально расширить этот файл, паттерн (get_connection + CREATE TABLE IF NOT
EXISTS) останется тем же.
"""
import sqlite3
import json
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "hackathon.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # позволяет обращаться к колонкам по имени: row["text"]
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL,
            data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_message(session_id: str, role: str, content: str) -> None:
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (session_id, role, content, datetime.datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def get_history(session_id: str, limit: int = 20) -> list[dict]:
    """Возвращает историю сообщений в формате, готовом для OpenAI API:
    [{"role": "user"/"assistant", "content": "..."}]"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC LIMIT ?",
        (session_id, limit),
    ).fetchall()
    conn.close()
    return [{"role": row["role"], "content": row["content"]} for row in rows]


def add_item(item_type: str, data: dict) -> int:
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO items (item_type, data, created_at) VALUES (?, ?, ?)",
        (item_type, json.dumps(data, ensure_ascii=False), datetime.datetime.utcnow().isoformat()),
    )
    conn.commit()
    item_id = cur.lastrowid
    conn.close()
    return item_id


def list_items(item_type: str | None = None) -> list[dict]:
    conn = get_connection()
    if item_type:
        rows = conn.execute(
            "SELECT * FROM items WHERE item_type = ? ORDER BY id DESC", (item_type,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "type": row["item_type"],
            "data": json.loads(row["data"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
