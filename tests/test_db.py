import sqlite3
import src.database.db as db
import pytest

TEST_DB = "data/test_app.db"


@pytest.fixture
def temp_db_path(tmp_path):
    return str(tmp_path / "test_app.db")


@pytest.fixture
def initialized_db(temp_db_path):
    db.init_db(temp_db_path)
    return temp_db_path


def test_get_conn_sets_row_factory(temp_db_path):
    conn = db.get_conn(temp_db_path)
    try:
        assert conn is not None
        assert conn.row_factory == sqlite3.Row
    finally:
        conn.close()


def test_init_db_creates_tables(temp_db_path):
    db.init_db(temp_db_path)

    conn = sqlite3.connect(temp_db_path)
    try:
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cur.fetchall()}
        assert "Predictions" in tables
        assert "Logs" in tables
        assert "Users" in tables
    finally:
        conn.close()


def test_insert_prediction_returns_id_and_fetch_latest(initialized_db):
    row_id = db.insert_prediction(
        source="api",
        mode="electrical",
        fault_type="Hotspot",
        confidence=0.91,
        image_path=None,
        input_json='{"a":1}',
        db_path=initialized_db,
    )

    assert isinstance(row_id, int)
    assert row_id > 0

    rows = db.fetch_latest(limit=10, db_path=initialized_db)
    assert len(rows) == 1
    assert rows[0]["id"] == row_id
    assert rows[0]["source"] == "api"
    assert rows[0]["mode"] == "electrical"
    assert rows[0]["fault_type"] == "Hotspot"
    assert abs(rows[0]["confidence"] - 0.91) < 1e-9


def test_fetch_latest_respects_limit(initialized_db):
    for i in range(3):
        db.insert_prediction(
            source="api",
            mode="image",
            fault_type=f"F{i}",
            confidence=0.5,
            db_path=initialized_db,
        )

    rows = db.fetch_latest(limit=2, db_path=initialized_db)
    assert len(rows) == 2
    # Newest first
    assert rows[0]["id"] > rows[1]["id"]


def test_insert_log_and_fetch_logs(initialized_db):
    log_id = db.insert_log(
        level="ERROR",
        logger_name="TestLogger",
        module="test_module",
        message="Something broke",
        func_name="test_func",
        line_no="123",
        exception="ValueError",
        db_path=initialized_db,
    )

    assert log_id > 0

    logs = db.fetch_logs(limit=10, db_path=initialized_db)
    assert len(logs) == 1
    assert logs[0]["id"] == log_id
    assert logs[0]["level"] == "ERROR"
    assert logs[0]["message"] == "Something broke"


def test_create_user_and_get_user_by_username(monkeypatch, initialized_db):

    # Force to ignore admin
    monkeypatch.setattr(db, "DB_PATH", initialized_db)

    suffix = str(id(initialized_db))
    username = f"alice_{suffix}"
    email = f"alice_{suffix}@example.com"

    user_id = db.create_user(
        user_type="Admin", username=username, email=email, password="secret123"
    )
    assert user_id > 0

    row = db.get_user_by_username(username)
    assert row is not None
    assert row["username"] == username
    assert row["email"] == email
    assert row["type"] == "Admin"
    assert row["password_hash"] != "secret123"
