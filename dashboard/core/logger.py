import logging  # built-in logging module

class Logger:
    """
    Logger utility class providing a central logging mechanism
    across the Solar PV Fault Detection/Rectification system.

    Follows a Singleton-like design to ensure that only one logger
    instance is created and shared across all modules.
    """

    __logger = None  # shared across all instances

    @staticmethod
    def get_logger(name: str = "SolarPVLogger") -> logging.Logger:
        """
        Returns a configured logger instance.

        Args:
            name (str): Name of the logger instance (default is 'SolarPVLogger').

        Returns:
            Configured logger object
        """
        if Logger.__logger is None:  # first call creates logger
            logging.basicConfig(
                level = logging.INFO,
                format = "%(asctime)s | %(levelname)s | %(message)s"
            )
            Logger.__logger = logging.getLogger(name)
        return Logger.__logger
