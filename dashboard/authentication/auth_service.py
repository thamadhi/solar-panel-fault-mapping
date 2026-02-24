from dashboard.database.db import get_user_by_username
from dashboard.authentication.security import verify_password
from dashboard.models.user import User
from dashboard.database.user_repo import create_user, username_exists, email_exists


def login(username: str, password: str) -> User | None:
    row = get_user_by_username(username=username)
    if row is None:
        return None

    if not verify_password(password, row["password_hash"]):
        return None

    # Build the correct User from DB details
    return User(
        id=row["id"],
        type=row["type"],
        username=row["username"],
        email=row["email"]
    )


def register_user(user_type: str, username: str, email: str, password: str) -> tuple[bool, str]:
    if len(username.strip()) < 3:
        return False, "Username must be at least 3 characters."

    if "@" not in email or "." not in email:
        return False, "Please enter a valid email."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if username_exists(username):
        return False, "Username already exists."

    if email_exists(email):
        return False, "Email already exists."

    create_user(user_type=user_type, username=username.strip(), email=email.strip(), password=password)
    return True, "User registered successfully."
