import time
import jwt
import pytest

import src.authentication.jwt_utils as jwt_utils


def test_create_and_verify_token_success():
    """
    Test that. JWT token can be created and verified successfully.

    Steps:
    1. Create a token with user_id, username, and role.
    2. Verify the token using jwt_utils.verify_token.
    3. Assert that the decoded token contains the correct fields.
    """
    token = jwt_utils.create_token(user_id=1, username="alice", role="Admin")

    decoded = jwt_utils.verify_token(token)

    assert decoded["sub"] == "1"
    assert decoded["username"] == "alice"
    assert decoded["role"] == "Admin"
    assert "iat" in decoded  # Issued-at timestamp exists
    assert "exp" in decoded  # Expiration timestamp exists


def test_invalid_token_raises():
    """
    Test that verifying an invalid JWT token raises an exception.

    - Provide a malformed token string.
    - Expect a jwtInvalidTokenError to be raised.
    """
    with pytest.raises(jwt.InvalidTokenError):
        jwt_utils.verify_token("this.is.not.a.valid.token")


def test_expired_token_raises(monkeypatch):
    """
    Test that a token with a very short expiration correctly
    raises ExpiredSignatureError.

    Steps:
    1. Temporarily set JWT expiration to 1 second using monkeypatch.
    2. Create a token.
    3. Wait 2 seconds so the token expires.
    4. Verify that jwt_utils.verify_token raises jwt.ExpiredSignatureError.
    """
    # Temporarily reduce expiration to 1 second
    monkeypatch.setattr(jwt_utils, "JWT_EXP_SECONDS", 1)

    token = jwt_utils.create_token(user_id=2, username="bob", role="User")

    # Wait until it expires
    time.sleep(2)

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt_utils.verify_token(token)


def test_token_contains_correct_expiration(monkeypatch):
    """
    Test that the JWT token contains the correct expiration timestamp.

    Steps:
    1. Set JWT expiration to 3600 seconds (1 hour) using monkeypatch.
    2. Create a token and decode it.
    3. Check that the 'exp' field is roughly now + 3600 seconds.
    """
    monkeypatch.setattr(jwt_utils, "JWT_EXP_SECONDS", 3600)

    before = int(time.time())
    token = jwt_utils.create_token(3, "charlie", "User")
    decoded = jwt_utils.verify_token(token)
    after = int(time.time())

    # Expiration about now + 3600
    assert before + 3590 <= decoded["exp"] <= after + 3610
