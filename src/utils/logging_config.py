"""
Logging configuration for the Real Estate AI System.
Provides structured logging with different handlers for different severity levels.
"""

import logging
import logging.handlers
import os
from pathlib import Path

def setup_logging(log_dir: str = "logs", log_level: str = "INFO") -> None:
    """
    Configure logging for the application with both file and console handlers.
    
    Args:
        log_dir (str): Directory to store log files
        log_level (str): Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Set up formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for all logs (DEBUG and above)
    all_logs_file = os.path.join(log_dir, 'all.log')
    file_handler = logging.handlers.RotatingFileHandler(
        all_logs_file, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # File handler for errors (ERROR and above)
    error_logs_file = os.path.join(log_dir, 'error.log')
    error_handler = logging.handlers.RotatingFileHandler(
        error_logs_file, maxBytes=10*1024*1024, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name (str): Name for the logger, typically __name__ of the module
        
    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)
