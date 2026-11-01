import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    
    # Create logs folder if it does not exist
    log_directory = "logs"
    os.makedirs(log_directory, exist_ok=True)
    
    log_file = os.path.join(log_directory, "pipeline.log")
    
    # Log format
    log_format = (
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    )
    
    formatter = logging.Formatter(log_format)
    
    # Save logs to file, rotating after 5 MB
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )
    
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Also display logs in terminal
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Configure logger
    logger = logging.getLogger("ecommerce_pipeline")
    logger.setLevel(logging.INFO)
    
    # Avoid adding duplicate handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

