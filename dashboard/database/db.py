import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from dashboard.authentication.security import hash_password

DB_PATH = "data/app.db"


def get_conn(db_path: str = DB_PATH) -> sqlite3.Connection:
    """
    Creates and returns a SQLite database connection.

    The connection uses a `sqlite3.Row` as the row factory so that
    query results can be accessed like dictionaries.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        sqlite3.Connection: An active SQLite connection object.
    """

    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """
    Initializes the database schema.

    Creates the `Predictions` table if it does not already exist.
    This function should be called once during the application startup.

    Args:
        db_path (str): Path to the SQLite database file.

    Returns:
        None.
    """
    # Ensure folder exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            level TEXT NOT NULL,
            logger_name TEXT,
            module TEXT,
            func_name TEXT,
            line_no INTEGER,
            message TEXT,
            exception TEXT        
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL        
        )
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
        db_path: str = DB_PATH
    ) -> int:
    """
    Inserts a new fault record into the database.

    Stores metadata about a prediction including source,
    detection mode, predicted fault type, model confidence,
    image path, and JSON input data.

    Args:
        source (str): Origin of the dashboard (e.g., "api").
        mode (str): Prediction mode (e.g., "electrical", "image").
        fault_type (str): Predicted fault classification label.
        confidence (float): Model confidence score (0.0-1.0).
        image_path (Optional[str]): File path to the analysed image.
        input_json (Optional[str]): JSON input features.
        db_path (str): Path to the SQLite database file.

    Returns:
        int: ID of the newly inserted database record.
    """

    conn = get_conn(db_path)
    cur = conn.cursor()

    created_at = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO Predictions (created_at, source, mode, fault_type,
        confidence, image_path, input_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (created_at, source, mode, fault_type, float(confidence),
          image_path, input_json))

    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return int(row_id)


def fetch_latest(limit: int = 50, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """
    Retrieves the most recent prediction records.

    Results are ordered by newest first.

    Args:
        limit (int): Maximum number of records to retrieve.
        db_path (str): Path to the SQLite database file.

    Returns:
        List[Dict[str, Any]]: A list of prediction records as dictionaries.
    """

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


def insert_log(
        level: str,
        logger_name: str,
        module: str,
        message: str,
        func_name: str,
        line_no: str,
        exception: str,
        db_path: str = DB_PATH
    ) -> int:

    conn = get_conn(db_path)
    cur = conn.cursor()

    created_at = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO Logs
        (created_at, level, logger_name, module, func_name, line_no, message, exception)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (created_at, level, logger_name, module, func_name, line_no, message, exception))

    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return int(row_id)


def fetch_logs(limit: int = 100, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """
    Fetch latest logs, newest first.
    """

    conn = get_conn(db_path)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, created_at, level, logger_name, module, func_name, line_no, message, exception
        FROM Logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def create_user(user_type: str, username: str, email: str, password: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Users(type, username, email, password_hash) VALUES (?, ?, ?, ?)",
        (user_type, username, email, hash_password(password))
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_user_by_username(username: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM Users WHERE username = ?", (username,)
    )
    row = cur.fetchone()
    conn.close()
    return row


def create_default_admin():
    existing = get_user_by_username("admin")
    if existing is None:
        create_user(
            user_type="Admin",
            username="admin",
            email="admin@solar.com",
            password="admin123"
        )

def fetch_latest_faults(limit: int = 5) -> List[Dict[str, Any]]:

    conn = get_conn()
    rows = conn.execute(
        """
        SELECT id, created_at, source, mode, fault_type, confidence
        FROM Predictions
        ORDER BY datetime(created_at) DESC
        LIMIT ?
        """, (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_fault_trend_daily(days: int = 30) -> List[Dict[str, Any]]:

    conn = get_conn()
    rows = conn.execute(
        """
        SELECT date(created_at) AS day, COUNT(*) AS count
        FROM Predictions
        WHERE date(created_at) >= date('now', ?)
        GROUP BY date(created_at)
        ORDER BY day ASC
        """, (f"-{days} days",)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
