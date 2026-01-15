import logging  # built-in logging module

class Logger:
    """
    Logger utility class providing a central logging mechanism
    across the Solar PV Fault Detection/Rectification system.

    Follows a Singleton-like design to ensure that only one logger
    instance is created and shared across all modules.
    """

    _logger = None  # shared across all instances

    @staticmethod
    def get_logger(name: str = "SolarPVLogger") -> logging.Logger:
        """
        Returns a configured logger instance.
        
        name : str, optional
            Name of the logger instance (default is 'SolarPVLogger').

        return : logging.Logger
            Configured logger object
        """
        if Logger._logger is None:  # first call creates logger
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s | %(levelname)s | %(message)s"
            )
            Logger._logger = logging.getLogger(name)
        return Logger._logger
