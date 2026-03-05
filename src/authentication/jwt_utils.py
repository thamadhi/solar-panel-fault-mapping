import os
import time
import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "a_very_long_random_secret_key_at_least_32_chars")
JWT_ALGO = "HS256"
JWT_EXP_SECONDS = 60 * 60 * 24  # 24 hours


def create_token(user_id: int, username: str, role: str) -> str:
    """
    Generates a JWT Web Token (JWT) for an authenticated user.

    This function creates a signed JWT containing basic user identity
    information and an expiration time. The token can later be used to
    authenticate requests.    
    
    Args:
        user_id (int): Unique identifier of the user.
        username (str): Username of the authenticated user.
        role (str): Role or permission of the user.

    Returns:
        str: A signed JWT token string.
    """

    payload = {
        "sub": str(user_id),    # Subject (user identifier)
        "username": username,
        "role": role,
        "iat": int(time.time()),    # Issued at time
        "exp": int(time.time()) + JWT_EXP_SECONDS   # Expiration time
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def verify_token(token: str) -> dict:
    """
    Verify and decode a JSON Web Token (JWT).

    This function checks the token's signature and expiration time
    using the configured secret and algorithm. If valid, the decoded
    payload containing user information is returned.

    Args:
        token (str): the JWT token provided by the client.

    Returns:
        dict: The decoded token payload containing user information.

    Raises:
        jwt.ExpirationSignatureError: if the token has expired.
        jwt.InvalidTokenError: If the token is invalid.    
    """

    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
