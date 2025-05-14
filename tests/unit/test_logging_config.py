"""Unit tests for the logging_config module."""

import os
import json
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the module to test
from src.utils.logging_config import (
    setup_logging,
    get_logger,
    JsonFormatter,
    setup_service_logging
)

class TestLoggingConfig(unittest.TestCase):
    """Test cases for the logging_config module."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for log files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_dir = self.temp_dir.name
        
        # Reset the root logger before each test
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[::]:
            root_logger.removeHandler(handler)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up the temporary directory
        self.temp_dir.cleanup()
    
    def test_setup_logging_creates_log_directory(self):
        """Test that setup_logging creates the log directory."""
        # Create a subdirectory path that doesn't exist
        log_subdir = os.path.join(self.log_dir, "test_logs")
        
        # Call setup_logging
        setup_logging(log_dir=log_subdir, log_level="INFO")
        
        # Check that the directory was created
        self.assertTrue(os.path.exists(log_subdir))
    
    def test_setup_logging_creates_service_directory(self):
        """Test that setup_logging creates a service-specific log directory."""
        # Define a service name
        service_name = "test_service"
        
        # Call setup_logging with a service name
        setup_logging(service_name=service_name, log_dir=self.log_dir, log_level="INFO")
        
        # Check that the service directory was created
        service_dir = os.path.join(self.log_dir, service_name)
        self.assertTrue(os.path.exists(service_dir))
    
    def test_setup_logging_creates_log_files(self):
        """Test that setup_logging creates the expected log files."""
        # Call setup_logging
        setup_logging(log_dir=self.log_dir, log_level="INFO")
        
        # Check that the log files were created
        self.assertTrue(os.path.exists(os.path.join(self.log_dir, "all.log")))
        self.assertTrue(os.path.exists(os.path.join(self.log_dir, "error.log")))
    
    def test_setup_logging_creates_service_log_file(self):
        """Test that setup_logging creates a service-specific log file."""
        # Define a service name
        service_name = "test_service"
        
        # Call setup_logging with a service name
        setup_logging(service_name=service_name, log_dir=self.log_dir, log_level="INFO")
        
        # Check that the service log file was created
        service_dir = os.path.join(self.log_dir, service_name)
        self.assertTrue(os.path.exists(os.path.join(service_dir, f"{service_name}.log")))
    
    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        # Call get_logger
        logger = get_logger("test_logger")
        
        # Check that a logger was returned
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")
    
    def test_get_logger_with_extra_adds_filter(self):
        """Test that get_logger with extra adds a filter to the logger."""
        # Call get_logger with extra
        logger = get_logger("test_logger", {"key": "value"})
        
        # Check that a filter was added
        self.assertEqual(len(logger.filters), 1)
    
    def test_json_formatter_formats_record(self):
        """Test that JsonFormatter formats a log record as JSON."""
        # Create a formatter
        formatter = JsonFormatter()
        
        # Create a log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test_path",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Format the record
        formatted = formatter.format(record)
        
        # Check that the result is valid JSON
        log_data = json.loads(formatted)
        
        # Check that the expected fields are present
        self.assertEqual(log_data["name"], "test_logger")
        self.assertEqual(log_data["level"], "INFO")
        self.assertEqual(log_data["message"], "Test message")
        self.assertEqual(log_data["lineno"], 42)
    
    def test_json_formatter_includes_exception_info(self):
        """Test that JsonFormatter includes exception info in the formatted record."""
        # Create a formatter
        formatter = JsonFormatter()
        
        try:
            # Raise an exception
            raise ValueError("Test exception")
        except ValueError as e:
            # Create a log record with exception info
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test_path",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=(ValueError, e, e.__traceback__)
            )
        
        # Format the record
        formatted = formatter.format(record)
        
        # Check that the result is valid JSON
        log_data = json.loads(formatted)
        
        # Check that exception info is included
        self.assertIn("exception", log_data)
        self.assertEqual(log_data["exception"]["type"], "ValueError")
        self.assertEqual(log_data["exception"]["message"], "Test exception")
    
    def test_setup_service_logging_returns_function(self):
        """Test that setup_service_logging returns a function."""
        # Call setup_service_logging
        get_service_logger = setup_service_logging("test_service", log_level="INFO")
        
        # Check that a function was returned
        self.assertTrue(callable(get_service_logger))
    
    def test_service_logger_creates_qualified_name(self):
        """Test that the service logger creates a qualified name."""
        # Call setup_service_logging
        get_service_logger = setup_service_logging("test_service", log_level="INFO")
        
        # Get a logger for a module
        logger = get_service_logger("test_module")
        
        # Check that the logger has a qualified name
        self.assertEqual(logger.name, "test_service.test_module")

if __name__ == "__main__":
    unittest.main()
