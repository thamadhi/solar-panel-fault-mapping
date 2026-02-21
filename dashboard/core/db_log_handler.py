import logging
from typing import Optional
from db import insert_log


class DBLogHandler(logging.Handler):
    """
    Logging handler that writes log records into SQLite using db.py.
    """

    def __init__(self, db_path: str = "data/app.db") -> None:
        super().__init__()
        self.db_path = db_path

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)

            exc: Optional[str] = None
            if record.exc_info:
                exc = self.formatException(record.exc_info)

            insert_log(
                level=record.levelname,
                logger_name=record.name,
                message=msg,
                module=record.module,
                func_name=record.funcName,
                line_no=record.lineno,
                exception=exc,
                db_path=self.db_path
            )

        except Exception:
            self.handleError(record)
