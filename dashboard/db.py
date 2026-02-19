import sqlite3
from datetime import datetime

DB_PATH = "dashboard/data/app.db"

def get_conn(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Predictions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          created_at TEXT NOT NULL,
          mode TEXT,
          fault_type TEXT NOT NULL,      
          confidence REAL NOT NULL
        );
    """)

    conn.commit()
    conn.close()
