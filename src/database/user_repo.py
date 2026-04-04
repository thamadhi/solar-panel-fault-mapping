from src.database.db import (
    db_create_user,
    db_username_exists,
    db_email_exists
)


def register_user(user_type: str, username: str, email: str, password: str):
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
