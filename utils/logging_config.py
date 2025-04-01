"""Centralized logging configuration for the Real Estate AI Bot"""
import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging(
    log_level=logging.INFO,
    log_dir="logs",
    app_name="real_estate_bot",
    max_bytes=10_000_000,  # 10MB
    backup_count=5
):
    """Set up logging with rotation to prevent disk space issues.
    
    Args:
        log_level: Logging level (default: INFO)
        log_dir: Directory to store log files (default: logs)
        app_name: Name of the application for log file naming
        max_bytes: Maximum size of each log file before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Set up rotating file handler
    log_file = log_path / f"{app_name}.log"
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    
    # Set up console handler
    console_handler = logging.StreamHandler()
    
    # Create formatters and add it to the handlers
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Get the root logger and set its level
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers and add our handlers
    root_logger.handlers = []
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create a logger for this module
    logger = logging.getLogger(__name__)
    logger.info(f"Logging setup complete. Log file: {log_file}")
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    Args:
        name: Name for the logger (typically __name__ from the calling module)
    
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
