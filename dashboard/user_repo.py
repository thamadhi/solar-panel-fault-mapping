# dashboard/user_repo.py
from dashboard.db import get_conn
from dashboard.security import hash_password

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

def username_exists(username: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM Users WHERE username = ? LIMIT 1", (username,))
    ok = cur.fetchone() is not None
    conn.close()
    return ok

def email_exists(email: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM Users WHERE email = ? LIMIT 1", (email,))
    ok = cur.fetchone() is not None
    conn.close()
    return ok
