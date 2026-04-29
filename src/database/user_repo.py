from src.database.db import (
    db_create_user,
    db_username_exists,
    db_email_exists
)
from typing import Any

def register_user(user_type: str, username: str, email: str, password: str) -> tuple[bool, Any]:
    """
    Registers a new user in the system.

    This function checks if the provided username or email already exists.
    If either exists, registration fails with an appropriate message.
    Otherwise, it creates a new user record in the database.

    Args:
        user_type (str): Type of user (e.g., "Admin").
        username (str): Desired username (must be unique).
        email (str): Email address of the user (must be unique).
        password (str): Plain-text password to be hashed and stored.

    Returns:
        tuple[bool, Any]: A tuple containing:
            - bool: True if registration succeeded, False if failed.
            - Any: User ID of the newly created user if successful, or
                   an error message string if registration failed.
    """
    if db_username_exists(username):
        return False, "Username already exists"

    if db_email_exists(email):
        return False, "Email already exists"

    user_id = db_create_user(
        user_type,
        username,
        email,
        password
    )

    return True, user_id
