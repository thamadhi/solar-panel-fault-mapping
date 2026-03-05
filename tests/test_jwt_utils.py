import time
import jwt
import pytest

import src.authentication.jwt_utils as jwt_utils


def test_create_and_verify_token_success():
    token = jwt_utils.create_token(user_id=1, username="alice", role="Admin")

    decoded = jwt_utils.verify_token(token)

    assert decoded["sub"] == "1"
    assert decoded["username"] == "alice"
    assert decoded["role"] == "Admin"
    assert "iat" in decoded
    assert "exp" in decoded


def test_invalid_token_raises():
    with pytest.raises(jwt.InvalidTokenError):
        jwt_utils.verify_token("this.is.not.a.valid.token")


def test_expired_token_raises(monkeypatch):

    # Temporarily reduce expiration to 1 second
    monkeypatch.setattr(jwt_utils, "JWT_EXP_SECONDS", 1)

    token = jwt_utils.create_token(user_id=2, username="bob", role="User")

    # Wait until it expires
    time.sleep(2)

    with pytest.raises(jwt.ExpiredSignatureError):
        jwt_utils.verify_token(token)


def test_token_contains_correct_expiration(monkeypatch):
    monkeypatch.setattr(jwt_utils, "JWT_EXP_SECONDS", 3600)

    before = int(time.time())
    token = jwt_utils.create_token(3, "charlie", "User")
    decoded = jwt_utils.verify_token(token)
    after = int(time.time())

    # Expiration about now + 3600
    assert before + 3590 <= decoded["exp"] <= after + 3610
