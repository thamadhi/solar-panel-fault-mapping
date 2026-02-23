import hashlib
import os

def hash_password(password: str, salt: bytes | None = None):
    if salt is None:

        # Create a 16 byte random salt, else always same hash for passwords
        salt = os.urandom(16)

    # Encoded password converted to bytes
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)

    # Convert to hex to store in database easily as text
    return salt.hex() + ":" + hashed.hex()


def verify_password(password: str, stored: str) -> bool:
    salt_hex, hash_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    test = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
    return test.hex() == hash_hex
