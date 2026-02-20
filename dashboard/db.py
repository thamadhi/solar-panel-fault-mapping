import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = "data/app.db"

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
            source TEXT,
            mode TEXT,
            fault_type TEXT NOT NULL,      
            confidence REAL NOT NULL,
            image_path TEXT,
            input_json TEXT
        );
    """)

    conn.commit()
    conn.close()


def insert_prediction(
        source: str,
        mode: str,
        fault_type: str,
        confidence: float,
        image_path: Optional[str] = None,
        input_json: Optional[str] = None,
        db_path = DB_PATH
    ) -> int:

    conn = get_conn(db_path)
    cur = conn.cursor()

    created_at = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO Predictions (created_at, source, mode, fault_type, confidence, image_path, input_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (created_at, source, mode, fault_type, float(confidence), image_path, input_json))

    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return int(row_id)


def fetch_latest(limit: int = 50, db_path = DB_PATH) -> List[Dict[str, Any]]:
    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, created_at, source, mode, fault_type, confidence, image_path
        FROM Predictions
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]
