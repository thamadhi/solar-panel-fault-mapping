import logging
from dashboard.core.db_log_handler import DBLogHandler
import sqlite3

def test_logger():

    logger = logging.getLogger("manual_test_logger")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers during multiple runs
    logger.handlers.clear()

    db_handler = DBLogHandler(db_path="data/app.db")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    db_handler.setFormatter(formatter)
    logger.addHandler(db_handler)

    # Send logs
    logger.info("This is a test INFO log")
    logger.warning("This is a test WARNING log")

    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("Test exception log")

    # ---- VERIFY DB CONTENT ----
    conn = sqlite3.connect("data/app.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT level, logger_name, message, exception
        FROM Logs
        WHERE logger_name = 'manual_test_logger'
        ORDER BY id DESC
        LIMIT 3
    """)

    rows = cur.fetchall()
    conn.close()

    print(rows)

    assert len(rows) >= 3
    assert any("INFO" in r[0] for r in rows)
    assert any("WARNING" in r[0] for r in rows)
    assert any("ERROR" in r[0] for r in rows)