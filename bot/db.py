# db.py
import sqlite3
import json
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "posts.db")
IMAGE_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

def _get_conn():
    return sqlite3.connect(DB_PATH)

def create_tables():
    with _get_conn() as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            title TEXT NOT NULL,
            specs TEXT NOT NULL,
            caption TEXT NOT NULL,
            photos_json TEXT NOT NULL   -- JSON list of filenames
        )
        """)
        conn.commit()

def add_post(title, specs, caption, photos):
    """
    Создаёт пост и возвращает его id.
    photos — список имён файлов (jpg, png), сохранённых в images/.
    """
    created_at = datetime.now().isoformat()
    with _get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO posts (created_at, title, specs, caption, photos_json) VALUES (?, ?, ?, ?, ?)",
            (created_at, title, specs, caption, json.dumps(photos, ensure_ascii=False))
        )
        conn.commit()
        return c.lastrowid

def get_post(post_id):
    with _get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id, created_at, title, specs, caption, photos_json FROM posts WHERE id = ?", (post_id,))
        row = c.fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "created_at": row[1],
        "title": row[2],
        "specs": row[3],
        "caption": row[4],
        "photos": json.loads(row[5]),
    }

def get_recent_posts(hours=24):
    """Список постов за последние `hours` часов (свежие сверху)."""
    threshold = datetime.now() - timedelta(hours=hours)
    with _get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT id, created_at, title, specs, caption, photos_json FROM posts ORDER BY id DESC")
        rows = c.fetchall()
    out = []
    for r in rows:
        created = datetime.fromisoformat(r[1])
        if created >= threshold:
            out.append({
                "id": r[0],
                "created_at": r[1],
                "title": r[2],
                "specs": r[3],
                "caption": r[4],
                "photos": json.loads(r[5]),
            })
    return out
