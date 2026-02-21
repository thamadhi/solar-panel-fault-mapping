import logging
from db import init_db
from .db_log_handler import DBLogHandler

class LoggerFactory:
    """
    A factory class for setting up and retrieving loggers with a centralized
    configuration.

    - Sets up logging once at application startup using a YAML configuration.
    - Ensures all loggers have the same handlers, formatters, and levels.
    - Provides pre-configured loggers for any module by name.

    Usage:
        # At app startup
        LoggerFactory.setup()

        # In modules
        logger = LoggerFactory.get_logger(__name__)
    """

    _configured = False # Keeps track whether logging system has been set up

    @classmethod
    def setup(cls, db_path: str = "data/app.db", level: int = logging.INFO) -> None:
        """
        Configures the Python logging system using a YAML file.

        Args:
            cls: Refers to the class (LoggerFactory).
        """
        
        if not cls._configured:
            return
        
        init_db(db_path)

        # Configure root so all modules inherit this handler
        root = logging.getLogger()
        root.setLevel(level)

        # Remove Existing handlers
        for h in list(root.handlers):
            root.removeHandler(h)

        # AddDB handler
        db_handler = DBLogHandler(db_path=db_path)
        db_handler.setLevel(level)
        db_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

        root.addHandler(db_handler)

        cls._configured = True


    @staticmethod
    def get_logger(name: str = "solar-pv") -> logging.Logger:
        """Returns a pre-configured logger.
        
        Args:
            name (str): The name of the logger.

        Returns:
            logging.Logger: A configured logger object with the YAML setup.
        """
        return logging.getLogger(name)
