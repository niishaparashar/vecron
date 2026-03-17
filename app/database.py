import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "vecron.db")
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB_PATH)

def get_db():
    # Render can mount a persistent disk; DB_PATH lets the service use it.
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
