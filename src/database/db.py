import os
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.authentication.security import hash_password

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

    cur.execute("""
        CREATE TABLE IF NOT EXISTS PVSystems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            system_type TEXT,
            num_strings INTEGER DEFAULT 2,
            modules_per_string INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES Users(id)
        )
    """)

    migrate_users_table()

    conn.commit()
    conn.close()


def insert_prediction(
    source: str,
    mode: str,
    fault_type: str,
    confidence: float,
    image_path: Optional[str] = None,
    input_json: Optional[str] = None,
    db_path: str = DB_PATH,
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

    cur.execute(
        """
        INSERT INTO Predictions (created_at, source, mode, fault_type,
        confidence, image_path, input_json)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            created_at,
            source,
            mode,
            fault_type,
            float(confidence),
            image_path,
            input_json,
        ),
    )

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
    cur.execute(
        """
        SELECT id, created_at, source, mode, fault_type, confidence, image_path
        FROM Predictions
        ORDER BY id DESC
        LIMIT ?
    """,
        (limit,),
    )
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
    db_path: str = DB_PATH,
) -> int:
    """
    Insert a log record into the Logs table.

    Args:
        level (str): Log level (e..g, "INFO", "WARNING").
        logger_name (str): Name of the logger instance.
        module (str): Module/file where the log is originated.
        message (str): Log message content.
        func_name (str): Function name where the log occurred.
        line_no (str): Line number (as string) where the log occurred.
        exception (str): Exception details (stack trace or message).
        db_path (str): Path to the SQLite database file.

    Returns:
        int: ID of the newly inserted log record.

    """

    conn = get_conn(db_path)
    cur = conn.cursor()

    created_at = datetime.utcnow().isoformat()

    cur.execute(
        """
        INSERT INTO Logs
        (created_at, level, logger_name, module, func_name, line_no, message, exception)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            created_at,
            level,
            logger_name,
            module,
            func_name,
            line_no,
            message,
            exception,
        ),
    )

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
    cur.execute(
        """
        SELECT id, created_at, level, logger_name, module, func_name, line_no, message, exception
        FROM Logs
        ORDER BY id DESC
        LIMIT ?
    """,
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def db_create_user(user_type: str, username: str, email: str, password: str) -> int:
    conn = get_conn()
    cur = conn.cursor()

    created_at = datetime.utcnow().isoformat()


    cur.execute("""
        INSERT INTO Users(type, username, email, password_hash, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (user_type, username, email, hash_password(password), created_at))

    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id

def migrate_users_table():
    conn = get_conn()
    cur = conn.cursor()

    # Add new columns if they don't exist
    try:
        cur.execute("ALTER TABLE Users ADD COLUMN created_at TEXT")
    except:
        pass

    try:
        cur.execute("ALTER TABLE Users ADD COLUMN last_login TEXT")
    except:
        pass

    try:
        cur.execute("ALTER TABLE Users ADD COLUMN is_active INTEGER DEFAULT 1")
    except:
        pass

    conn.commit()
    conn.close()

def db_username_exists(username: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM Users WHERE username=?", (username,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


def db_email_exists(email: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM Users WHERE email=?", (email,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


def db_update_last_login(user_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE Users SET last_login=? WHERE id=?",
        (datetime.utcnow().isoformat(), user_id),
    )
    conn.commit()
    conn.close()


def get_user_by_username(username: str) -> sqlite3.Row | None:
    """
    Retrieves a user record by username.

    Args:
        username (str): The username to search for.

    Returns:
        sqlite3.Row | None:
            - sqlite3.Row (dict-like row) if the user exists.
            - None if no matching user is found
    """

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return row


def create_default_admin() -> None:
    """
    Ensures a default admin account exists.

    If a user with username "admin" does not exist, this function creates one
    using the default credentials:
        - username: admin
        - email: admin@solar.com
        - password: admin123

    Returns:
        None
    """
    existing = get_user_by_username("admin")
    if existing is None:
        db_create_user(
            user_type="Admin",
            username="admin",
            email="admin@solar.com",
            password="admin123",
        )

def fetch_latest_faults(limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch the most recent fault predictions.

    Args:
        limit (int): Maximum number of records to return.

    Returns:
        List[Dict[str, Any]]: A list of recent prediction records.
    """

    conn = get_conn()
    rows = conn.execute(
        """
        SELECT id, created_at, source, mode, fault_type, confidence
        FROM Predictions
        ORDER BY datetime(created_at) DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_fault_trend_daily(days: int = 30) -> List[Dict[str, Any]]:
    """
    Fetch daily fault trend counts over the last N days.

    Groups predictions by date (day) and returns the count for each day.

    Args:
        days (int): Number of days to include (default: 30).

    Returns:
        List[Dict[str, Any]]: A list like:
            [{"day": "YYYY-MM-DD", "count": 12}, ...]
    """

    conn = get_conn()
    rows = conn.execute(
        """
        SELECT date(created_at) AS day, COUNT(*) AS count
        FROM Predictions
        WHERE date(created_at) >= date('now', ?)
        GROUP BY date(created_at)
        ORDER BY day ASC
        """,
        (f"-{days} days",),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_pv_system(
    user_id: int,
    system_type: str,
    modules_per_string: int,
) -> tuple[bool, str]:
    """
    Insert or update a PV system for a user.
    """
    try:
        conn = get_conn()
        cur = conn.cursor()

        cur.execute("SELECT id FROM PVSystems WHERE user_id = ?", (user_id,))
        row = cur.fetchone()

        if row:
            cur.execute(
                """
                UPDATE PVSystems
                SET system_type = ?, num_strings = 2, modules_per_string = ?
                WHERE user_id = ?
                """,
                (system_type, modules_per_string, user_id),
            )
        else:
            cur.execute(
                """
                INSERT INTO PVSystems (user_id, system_type, num_strings, modules_per_string)
                VALUES (?, ?, 2, ?)
                """,
                (user_id, system_type, modules_per_string),
            )

        conn.commit()
        conn.close()
        return True, "PV system saved successfully."

    except Exception as e:
        return False, f"Failed to save PV system: {e}"


def get_pv_system_by_user_id(user_id: int) -> Optional[dict[str, Any]]:
    """
    Return the PV system for a given user, if available.
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, user_id, system_type, num_strings, modules_per_string
        FROM PVSystems
        WHERE user_id = ?
        """,
        (user_id,),
    )

    row = cur.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "system_type": row["system_type"],
        "num_strings": row["num_strings"],
        "modules_per_string": row["modules_per_string"],
    }
