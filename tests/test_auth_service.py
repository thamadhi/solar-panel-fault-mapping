from unittest.mock import MagicMock

import dashboard.authentication.auth_service as auth


class FakeRow(dict):
    """Behaves like an sqlite3.Row enough for row['key'] access."""
    pass


def test_login_user_not_found(monkeypatch):
    monkeypatch.setattr(auth, "get_user_by_username", lambda username: None)

    out = auth.login("alice", "pass")
    assert out is None


def test_login_wrong_password(monkeypatch):
    monkeypatch.setattr(
        auth,
        "get_user_by_username",
        lambda username: FakeRow({"id": 1, "type": "Admin", "username": "alice", "email": "a@b.com", "password_hash": "X"})
    )
    monkeypatch.setattr(auth, "verify_password", lambda password, stored: False)

    out = auth.login("alice", "wrong")
    assert out is None


def test_login_success_returns_user(monkeypatch):
    row = FakeRow({
        "id": 10,
        "type": "Admin",
        "username": "alice",
        "email": "alice@example.com",
        "password_hash": "HASHED"
    })

    monkeypatch.setattr(auth, "get_user_by_username", lambda username: row)
    monkeypatch.setattr(auth, "verify_password", lambda password, stored: True)

    out = auth.login("alice", "secret123")
    assert out is not None
    assert out.id == 10
    assert out.type == "Admin"
    assert out.username == "alice"
    assert out.email == "alice@example.com"


def test_register_user_username_too_short():
    ok, msg = auth.register_user("User", "ab", "x@y.com", "secret123")
    assert ok is False
    assert "at least 3" in msg


def test_register_user_invalid_email():
    ok, msg = auth.register_user(
        "Admin",
        "alice",
        "notanemail",
        "secret123"
    )
    assert ok is False
    assert "enter a valid email" in msg


def test_register_user_password_too_short():
    ok, msg = auth.register_user("User", "alice", "alice@example.com", "123")
    assert ok is False
    assert "at least 6" in msg


def test_register_user_username_exists(monkeypatch):
    monkeypatch.setattr(auth, "username_exists", lambda username: True)
    monkeypatch.setattr(auth, "email_exists", lambda email: False)

    ok, msg = auth.register_user("User", "alice", "alice@example.com", "secret123")
    assert ok is False
    assert "Username already exists" in msg


def test_register_user_email_exists(monkeypatch):
    monkeypatch.setattr(auth, "username_exists", lambda username: False)
    monkeypatch.setattr(auth, "email_exists", lambda email: True)

    ok, msg = auth.register_user("User", "alice", "alice@example.com", "secret123")
    assert ok is False
    assert "Email already exists" in msg


def test_register_user_success_calls_create_user(monkeypatch):
    monkeypatch.setattr(auth, "username_exists", lambda username: False)
    monkeypatch.setattr(auth, "email_exists", lambda email: False)


    create_mock = MagicMock()
    monkeypatch.setattr(auth, "create_user", create_mock)

    ok, msg = auth.register_user(
        "Admin",
        " alice ",
        " alice@example.com ",
        "secret123"
    )
    assert ok is True
    assert "successful" in msg

    create_mock.assert_called_once()
    kwargs = create_mock.call_args.kwargs
    assert kwargs["user_type"] == "Admin"
    assert kwargs["username"] == "alice"    # Stripped
    assert kwargs["email"] == "alice@example.com"   # Stripped
    assert kwargs["password"] == "secret123"
