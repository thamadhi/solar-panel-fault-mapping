# import logging  # built-in logging module
# from logging.handlers import RotatingFileHandler    # Grow indefinitely


# logger = logging.getLogger(__name__)    # Track the module generated the log
# logger.setLevel(logging.INFO)  # Record info and everything severe

# if not logger.handlers: # Prevent duplicate handlers
#     formatter = logging.Formatter(
#         "%(asctime)s | %(levelname)s | %(message)s"
#     )

#     # Console handler
#     console_handler = logging.StreamHandler()
#     console_handler.setFormatter(formatter)

#     # File handler
#     file_handler = RotatingFileHandler(
#         "solar_pv.log",
#         maxBytes=5*1024*1024,
#         backupCount=5
#     )
#     file_handler.setFormatter(formatter)

#     logger.addHandler(console_handler)
#     logger.addHandler(file_handler)
