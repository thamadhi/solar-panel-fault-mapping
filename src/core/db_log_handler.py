import logging
from typing import Optional
from src.database import insert_log


class DBLogHandler(logging.Handler):
    """
    A custom loggin handler that stores log records in a SQLite database.

    The handler uses the ``insert_log()`` function from ``src.database`` to
    save structured log information such as the log level, logger name, message,
    module, function name, line number, and exception details.

    Attributes:
        __db_path (str):
            Path to the SQLite database file where logs will be stored.
    """

    def __init__(self, db_path: str = "data/app.db") -> None:
        super().__init__()
        self.__db_path = db_path

    def emit(self, record: logging.LogRecord) -> None:
        """
        Process and store a log rcord in the database.

        Workflow:
            1. Format the log message using the attached formatter.
            2. Check whether the record contains exception information.
            3. Format the exception details if available.
            4. Insert all log details into the database using ``insert_log()``.
            5. If an error occurs during logging, handle it safely using
                ``handleError(record)``.

        Args:
            record (logging.LogRecord):
                The log record containing event details such as level,
                message, file name, function name, and line number.

        Returns:
            None
        """

        try:
            # Formatted message (includes timestamp)
            msg = self.format(record)

            exc: Optional[str] = None
            if record.exc_info:
                # formatException belongs to the formatter
                if self.formatter:
                    exc = self.formatter.formatException(record.exc_info)
                else:
                    exc = logging.Formatter().formatException(record.exc_info)

            insert_log(
                level=record.levelname,
                logger_name=record.name,
                message=msg,
                module=record.module,
                func_name=record.funcName,
                line_no=record.lineno,
                exception=exc,
                db_path=self.__db_path,
            )

        except Exception:
            self.handleError(record)
