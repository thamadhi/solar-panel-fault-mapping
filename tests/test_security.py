import pytest
import src.authentication.security as security


def test_hash_password_salt_and_hash():
    hashed = security.hash_password("secret123")

    assert isinstance(hashed, str)
    assert ":" in hashed

    salt_hex, hash_hex = hashed.split(":")
    assert len(salt_hex) == 32  # 16 bytes is 32 hex chars
    assert len(hash_hex) == 64  # SHA256 -> 32 bytes so 64 hex chars


def test_hash_password_uses_random_salt():
    h1 = security.hash_password("password")
    h2 = security.hash_password("password")

    assert h1 != h2  # Different salts → different hashes


def test_verify_password_success():
    password = "my_secure_password"
    stored = security.hash_password(password)

    assert security.verify_password(password, stored) is True


def test_verify_password_failure_wrong_password():
    stored = security.hash_password("correct_password")

    assert security.verify_password("wrong_password", stored) is False


def test_hash_with_given_salt_is_deterministic():

    # Fixed 16-byte salt
    salt = b"\x00" * 16

    h1 = security.hash_password("abc", salt=salt)
    h2 = security.hash_password("abc", salt=salt)

    # Same salt + same password = same hash
    assert h1 == h2


def test_verify_invalid_stored_format_raises():
    with pytest.raises(ValueError):
        security.verify_password("pass", "invalid_format_without_colon")
