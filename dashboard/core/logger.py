import os
import yaml
import logging
import logging.config
from pathlib import Path
from db import init_db
from db_log_handler import DBLogHandler

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
    def setup(cls, db_ath: str = "data/app.db") -> None:
        """
        Configures the Python logging system using a YAML file.

        Args:
            cls: Refers to the class (LoggerFactory).
        """



    @staticmethod
    def get_logger(name: str = "solar-pv") -> logging.Logger:
        """Returns a pre-configured logger.
        
        Args:
            name (str): The name of the logger.

        Returns:
            logging.Logger: A configured logger object with the YAML setup.
        """
        return logging.getLogger(name)
