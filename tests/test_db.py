import os
import sqlite3
import json
from pathlib import Path
from dashboard.database.db import (
    DB_PATH, get_conn, init_db,
    insert_prediction, fetch_latest,
    insert_log, fetch_logs
)
TEST_DB = "data/test_app.db"

def reset_test_db():
    os.makedirs("data", exist_ok=True)
    if Path(TEST_DB).exists():
        Path(TEST_DB).unlink()


def test_get_conn():
    reset_test_db()
    init_db(TEST_DB)

    conn = get_conn(TEST_DB)
    assert isinstance(conn, sqlite3.Connection)
    assert conn.row_factory is sqlite3.Row
    conn.close()
    print("✅ test_get_conn passed")


def test_init_db():
    reset_test_db()
    init_db(TEST_DB)

    assert Path(TEST_DB).exists(), "DB file was not created"

    conn = sqlite3.connect(TEST_DB)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cur.fetchall()}
    conn.close()

    assert "Predictions" in tables, "Predictions table missing"
    assert "Logs" in tables, "Logs table missing"
    print("✅ test_init_db passed")


def test_insert_prediction():
    reset_test_db()
    init_db(TEST_DB)

    row_id = insert_prediction(
        source="unit_test",
        mode="image",
        fault_type="single_hotspot",
        confidence=0.88,
        image_path="tests/img1.png",
        input_json=json.dumps({"a": 1}),
        db_path=TEST_DB
    )

    assert isinstance(row_id, int)
    assert row_id > 0
    print("✅ test_insert_prediction passed")


def test_fetch_latest():
    reset_test_db()
    init_db(TEST_DB)

    # Insert 3 predictions
    ids = []
    for i in range(3):
        ids.append(insert_prediction(
            source="unit_test",
            mode="image",
            fault_type="clean" if i % 2 == 0 else "single_hotspot",
            confidence=0.5 + i * 0.1,
            image_path=f"tests/img{i}.png",
            input_json=None,
            db_path=TEST_DB
        ))

    rows = fetch_latest(limit=2, db_path=TEST_DB)

    assert isinstance(rows, list)
    assert len(rows) == 2, "Should return 2 rows (limit=2)"
    assert rows[0]["id"] == ids[-1], "Newest should be first"
    assert rows[1]["id"] == ids[-2], "Second newest should be second"
    print("✅ test_fetch_latest passed")


def test_insert_log():
    reset_test_db()
    init_db(TEST_DB)

    log_id = insert_log(
        level="INFO",
        logger_name="unit_test_logger",
        module="test_db",
        message="hello log",
        func_name="test_insert_log",
        line_no=123,
        exception=None,
        db_path=TEST_DB
    )

    assert isinstance(log_id, int)
    assert log_id > 0
    print("✅ test_insert_log passed")


def test_fetch_logs():
    reset_test_db()
    init_db(TEST_DB)

    # insert 3 logs
    ids = []
    for i in range(3):
        ids.append(insert_log(
            level="INFO",
            logger_name="unit_test_logger",
            module="test_db",
            message=f"log {i}",
            func_name="test_fetch_logs",
            line_no=200 + i,
            exception=None,
            db_path=TEST_DB
        ))

    logs = fetch_logs(limit=2, db_path=TEST_DB)

    assert isinstance(logs, list)
    assert len(logs) == 2
    assert logs[0]["id"] == ids[-1], "Newest log should be first"
    assert logs[0]["message"] == "log 2"
    print("✅ test_fetch_logs passed")
