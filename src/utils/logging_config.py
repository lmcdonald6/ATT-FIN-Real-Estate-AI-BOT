"""
Enhanced logging configuration for the Real Estate AI System.
Provides structured logging with different handlers for different severity levels,
supporting both centralized and microservice-specific logging.
"""

import logging
import logging.handlers
import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union

def setup_logging(service_name: str = None, log_dir: str = "logs", log_level: str = "INFO", 
    json_format: bool = False, log_to_stdout: bool = True, log_to_file: bool = True,
    max_bytes: int = 10*1024*1024, backup_count: int = 5) -> None:
    """
    Configure logging for the application with both file and console handlers.
    
    Args:
        service_name (str, optional): Name of the microservice. If provided, logs will be stored in a service-specific directory.
        log_dir (str): Base directory to store log files
        log_level (str): Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format (bool): Whether to output logs in JSON format (useful for log aggregation)
        log_to_stdout (bool): Whether to log to standard output
        log_to_file (bool): Whether to log to files
        max_bytes (int): Maximum size of each log file before rotation
        backup_count (int): Number of backup files to keep
    """
    # Create service-specific log directory if service_name is provided
    if service_name:
        log_dir = os.path.join(log_dir, service_name)
    
    # Create logs directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Set up formatters
    if json_format:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(process)d - %(thread)d - %(message)s'
        )
    
    # Set up root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates when reconfiguring
    for handler in root_logger.handlers[::]:
        root_logger.removeHandler(handler)
    
    # Console handler (INFO and above)
    if log_to_stdout:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    if log_to_file:
        # File handler for all logs (DEBUG and above)
        all_logs_file = os.path.join(log_dir, 'all.log')
        file_handler = logging.handlers.RotatingFileHandler(
            all_logs_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # File handler for errors (ERROR and above)
        error_logs_file = os.path.join(log_dir, 'error.log')
        error_handler = logging.handlers.RotatingFileHandler(
            error_logs_file, maxBytes=max_bytes, backupCount=backup_count
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)
        
        # Service-specific log file if service_name is provided
        if service_name:
            service_logs_file = os.path.join(log_dir, f'{service_name}.log')
            service_handler = logging.handlers.RotatingFileHandler(
                service_logs_file, maxBytes=max_bytes, backupCount=backup_count
            )
            service_handler.setLevel(logging.DEBUG)
            service_handler.setFormatter(formatter)
            root_logger.addHandler(service_handler)
    
    # Log uncaught exceptions
    sys.excepthook = lambda exc_type, exc_value, exc_traceback: \
        root_logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

class JsonFormatter(logging.Formatter):
    """
    Format log records as JSON strings for better integration with log aggregation tools.
    """
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
            'process': record.process,
            'thread': record.thread,
            'module': record.module,
            'funcName': record.funcName,
            'lineno': record.lineno
        }
        
        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        # Add extra attributes if available
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
            
        return json.dumps(log_data)

def get_logger(name: str, extra: Dict[str, Any] = None) -> logging.Logger:
    """
    Get a logger instance with the specified name and optional extra context.
    
    Args:
        name (str): Name for the logger, typically __name__ of the module
        extra (Dict[str, Any], optional): Extra context to include in all log messages
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Add a filter to include extra context if provided
    if extra:
        class ContextFilter(logging.Filter):
            def filter(self, record):
                record.extra = extra
                return True
        
        logger.addFilter(ContextFilter())
        
    return logger

def setup_service_logging(service_name: str, log_level: str = "INFO"):
    """
    Set up logging for a specific microservice.
    
    Args:
        service_name (str): Name of the microservice
        log_level (str): Minimum logging level
    
    Returns:
        function: A function that returns a logger for the service
    """
    # Set up logging for the service
    setup_logging(
        service_name=service_name,
        log_dir="logs",
        log_level=log_level,
        json_format=True,
        log_to_stdout=True,
        log_to_file=True
    )
    
    # Return a function that creates loggers for this service
    def get_service_logger(module_name: str, extra: Dict[str, Any] = None) -> logging.Logger:
        # Create a fully qualified name for the logger
        logger_name = f"{service_name}.{module_name}"
        
        # Add service context to extra
        service_extra = {"service": service_name}
        if extra:
            service_extra.update(extra)
            
        return get_logger(logger_name, service_extra)
    
    return get_service_logger
