import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "assistant.db"


def _connect():
    DB_PATH.parent.mkdir(exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with _connect() as connection:
        connection.executescript("""CREATE TABLE IF NOT EXISTS stats (key TEXT PRIMARY KEY, value INTEGER NOT NULL); CREATE TABLE IF NOT EXISTS activity (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT, title TEXT, created_at TEXT);""")
        for key in ("questions", "quiz_score"):
            connection.execute("INSERT OR IGNORE INTO stats(key, value) VALUES(?, 0)", (key,))
        connection.commit()


def _increment(key: str, amount: int = 1):
    with _connect() as connection:
        connection.execute("UPDATE stats SET value = value + ? WHERE key = ?", (amount, key))
        connection.commit()


def increment_questions():
    _increment("questions")


def record_quiz_score(score: int):
    with _connect() as connection:
        connection.execute("UPDATE stats SET value = MAX(value, ?) WHERE key = 'quiz_score'", (score,))
        connection.commit()
    add_activity("🧠", f"Completed a quiz with {score}%")


def add_activity(kind: str, title: str):
    with _connect() as connection:
        connection.execute("INSERT INTO activity(kind, title, created_at) VALUES(?, ?, ?)", (kind, title, datetime.now().strftime("%b %d, %Y %H:%M")))
        connection.commit()


def get_dashboard_stats():
    with _connect() as connection:
        rows = connection.execute("SELECT key, value FROM stats").fetchall()
    values = {row["key"]: row["value"] for row in rows}
    materials = len([path for path in (DB_PATH.parent.parent / "uploads").glob("*") if path.suffix.lower() in {".pdf", ".txt", ".docx"}])
    return {"questions": values.get("questions", 0), "quiz_score": values.get("quiz_score", 0), "materials": materials}


def get_recent_activity():
    with _connect() as connection:
        return connection.execute("SELECT kind, title, created_at FROM activity ORDER BY id DESC LIMIT 6").fetchall()
