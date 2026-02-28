import os
import time
import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "a_very_long_random_secret_key_at_least_32_chars")
JWT_ALGO = "HS256"
JWT_EXP_SECONDS = 60 * 60 * 24  # 24 hours


def create_token(user_id: int, username: str, role: str) -> str:
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXP_SECONDS
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def verify_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
