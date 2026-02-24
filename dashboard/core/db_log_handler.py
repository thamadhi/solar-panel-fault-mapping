import logging
from typing import Optional
from dashboard.database import insert_log


class DBLogHandler(logging.Handler):
    """
    Logging handler that writes log records into SQLite using db.py.
    """

    def __init__(self, db_path: str = "data/app.db") -> None:
        super().__init__()
        self.__db_path = db_path

    def emit(self, record: logging.LogRecord) -> None:
        try:
            # Formatted message (includes timestamp)
            msg = self.format(record)

            exc: Optional[str] = None
            if record.exc_info:
                # formatException belongs to the formatter
                if self.formatter:
                    exc = self.formatter.formatException(record.exc_info)
                else:
                    # Fallback
                    exc = logging.Formatter().formatException(record.exc_info)

            insert_log(
                level=record.levelname,
                logger_name=record.name,
                message=msg,
                module=record.module,
                func_name=record.funcName,
                line_no=record.lineno,
                exception=exc,
                db_path=self.__db_path
            )

        except Exception:
            self.handleError(record)
