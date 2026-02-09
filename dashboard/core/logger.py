import os
import yaml
import logging
import logging.config
from pathlib import Path

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
    def setup(cls) -> None:
        """
        Configures the Python logging system using a YAML file.

        Args:
            cls: Refers to the class (LoggerFactory).
        """
        if not cls._configured:
            BASE_DIR = Path(__file__).resolve().parent
            config_path = BASE_DIR / "logging_config.yaml"
            os.makedirs(BASE_DIR.parent / "logs", exist_ok=True) # Rotating handler writes here
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)  # read YAML, convert to dictionary
                logging.config.dictConfig(config)   # Setup loggers, handlers
            cls._configured = True  # Prevent duplicate handlers


    @staticmethod
    def get_logger(name: str = "solar-pv") -> logging.Logger:
        """Returns a pre-configured logger.
        
        Args:
            name (str): The name of the logger.

        Returns:
            logging.Logger: A configured logger object with the YAML setup.
        """
        return logging.getLogger(name)
