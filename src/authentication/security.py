import hashlib
import os


def hash_password(password: str, salt: bytes | None = None):
    """
    Securely hash a plain text password using PBKDF2-HMAC (SHA-256).

    This function generates a cryptographic hash of the provided password.
    A random 16-byte salt is created if none is supplied, ensuring
    that identical passwords produce different hashes.

    Args:
        password (str): The password to be hashed.
        salt (bytes | None, optional): A salt value for hashing. If None,
            a new random salt is generated. Providing a salt is mainly used
            internally during verification.

    Returns:
        str: A string in the format "<salt_hex>:<hash_hex>"
            suitable for storage.
    """

    if salt is None:

        # Create a 16 byte random salt, else always same hash for passwords
        salt = os.urandom(16)

    # Encoded password converted to bytes with 120000 iterations
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)

    # Convert to hex to store in database easily as text
    return salt.hex() + ":" + hashed.hex()


def verify_password(password: str, stored: str) -> bool:
    """
    Verify a plaint text password against a stored salted hash.

    Args:
        password (str): The password provided during login.
        stored (str): The stored password string retrieved from the
            database formatted as "<salt_hex>:<hash_hex>".

    Returns:
        bool: True if the password matches the stored hash. False otherwise.
    """

    salt_hex, hash_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    test = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)

    return test.hex() == hash_hex
