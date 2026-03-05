from src.database.db import get_user_by_username
from src.authentication.security import verify_password
from src.models.user import User
from src.database.user_repo import create_user, username_exists, email_exists


def login(username: str, password: str) -> User | None:
    """
    Authenticates a user using their username and password.

    This function retrieves the user record from the database using the
    provided username. It then verifies the given password against the
    stored password hash.

    Args:
        username (str): The username of the user attempting to log in.
        password (str): The plaintext password provided by the user.

    Returns:
        User | None:
            - Returns a User object if the authentication us successful.
            - Returns None if the username dos not exist or the password is
            incorrect.
    """

    row = get_user_by_username(username=username)
    if row is None:
        return None

    if not verify_password(password, row["password_hash"]):
        return None

    # Build the correct User object from database details
    return User(
        id=row["id"], type=row["type"], username=row["username"], email=row["email"]
    )


def register_user(
    user_type: str, username: str, email: str, password: str
) -> tuple[bool, str]:
    """
    Registers a new user into the system.

    This function validates the provided user information, checks for
    existing usernames or emails, and creates a new user record in the
    database if all validations pass.

    Args:
        user_type (str): The role/type of the user (e.g., Admin/Technician)
        username (str): The desired username for the new account.
        email (str): The user's email address
        password (str): The user's plaintext password.

    Returns:
        tule[bool, str]:
            - True and a success message if the user is registered successfully.
            - False and an error message if validation fails.
    """

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

    create_user(
        user_type=user_type,
        username=username.strip(),
        email=email.strip(),
        password=password,
    )
    return True, "User registered successfully."
