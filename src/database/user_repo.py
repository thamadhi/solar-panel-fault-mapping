from src.database.db import get_conn
from src.authentication.security import hash_password


def create_user(user_type: str, username: str, email: str, password: str) -> int:
    """
    Creates a new user in the database:

    Args:
        user_type (str): Type of the user.
        username (str): Unique username
        email (str): User email address.
        password (str): Plain text password (will be securely hashed).

    Returns:
        int: The ID of the newly created user.
    """
    conn = get_conn()
    cur = conn.cursor()

    # Insert new user with hashed password
    cur.execute(
        "INSERT INTO Users(type, username, email, password_hash) VALUES (?, ?, ?, ?)",
        (user_type, username, email, hash_password(password))
    )
    conn.commit()
    user_id = cur.lastrowid
    conn.close()

    return user_id


def username_exists(username: str) -> bool:
    """
    Check if a username exists in the database.

    Args:
        username (str): Username to check.

    Returns:
        bool: If username exists, False otherwise.
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM Users WHERE username = ? LIMIT 1", (username,))
    ok = cur.fetchone() is not None
    conn.close()

    return ok


def email_exists(email: str) -> bool:
    """
    Check if an email address already exists in the database.

    Args:
        email (str): Email address to check.

    Returns:
        bool: True if email exists, False otherwise.
    """
    conn = get_conn()
    cur = conn.cursor()

    # Query database for exisiting mail
    cur.execute("SELECT 1 FROM Users WHERE email = ? LIMIT 1", (email,))
    ok = cur.fetchone() is not None
    conn.close()

    return ok
