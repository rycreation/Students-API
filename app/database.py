import sqlite3
from pathlib import Path
from app.config import DATABASE_PATH

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "students.db"

def get_connection():
   
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def add_role_column_if_missing(conn):
    columns = conn.execute(
        "PRAGMA table_info(users)"
    ).fetchall()

    column_names = {row["name"] for row in columns}

    if "role" not in column_names:
        conn.execute(
            "ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'user'"
        )
        conn.commit()


def init_db():
    conn = get_connection()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
                    CHECK(length(trim(name)) >= 2),
                email TEXT NOT NULL UNIQUE
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
                    CHECK(role IN ('user', 'admin'))
            )
        """)

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
