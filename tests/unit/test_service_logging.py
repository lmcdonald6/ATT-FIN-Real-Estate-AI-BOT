"""Unit tests for service-specific logging configuration."""

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

class TestServiceLogging(unittest.TestCase):
    """Test cases for the service-specific logging configuration."""
    
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
    
    def test_setup_service_logging_creates_service_directory(self):
        """Test that setup_service_logging creates a service-specific log directory."""
        # Define a service name
        service_name = "test_service"
        
        # Call setup_service_logging
        get_service_logger = setup_service_logging(service_name=service_name, log_level="INFO")
        
        # Check that the service directory was created
        service_dir = os.path.join("logs", service_name)
        self.assertTrue(os.path.exists(service_dir))
        
        # Clean up
        os.rmdir(service_dir)
        os.rmdir("logs")
    
    def test_service_logger_creates_qualified_name(self):
        """Test that the service logger creates a qualified name."""
        # Call setup_service_logging with a temporary log directory
        with patch('src.utils.logging_config.setup_logging') as mock_setup:
            get_service_logger = setup_service_logging("test_service", log_level="INFO")
            
            # Get a logger for a module
            logger = get_service_logger("test_module")
            
            # Check that the logger has a qualified name
            self.assertEqual(logger.name, "test_service.test_module")
    
    def test_service_logger_adds_service_context(self):
        """Test that the service logger adds service context to the logger."""
        # Call setup_service_logging with a temporary log directory
        with patch('src.utils.logging_config.setup_logging') as mock_setup:
            get_service_logger = setup_service_logging("test_service", log_level="INFO")
            
            # Get a logger for a module
            logger = get_service_logger("test_module")
            
            # Check that the logger has a filter
            self.assertEqual(len(logger.filters), 1)
            
            # Create a log record
            record = logging.LogRecord(
                name="test_service.test_module",
                level=logging.INFO,
                pathname="test_path",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=None
            )
            
            # Apply the filter
            logger.filters[0].filter(record)
            
            # Check that the service context was added
            self.assertTrue(hasattr(record, "extra"))
            self.assertEqual(record.extra["service"], "test_service")
    
    def test_service_logger_merges_extra_context(self):
        """Test that the service logger merges extra context with service context."""
        # Call setup_service_logging with a temporary log directory
        with patch('src.utils.logging_config.setup_logging') as mock_setup:
            get_service_logger = setup_service_logging("test_service", log_level="INFO")
            
            # Get a logger for a module with extra context
            extra = {"key": "value"}
            logger = get_service_logger("test_module", extra)
            
            # Check that the logger has a filter
            self.assertEqual(len(logger.filters), 1)
            
            # Create a log record
            record = logging.LogRecord(
                name="test_service.test_module",
                level=logging.INFO,
                pathname="test_path",
                lineno=42,
                msg="Test message",
                args=(),
                exc_info=None
            )
            
            # Apply the filter
            logger.filters[0].filter(record)
            
            # Check that the service context was added
            self.assertTrue(hasattr(record, "extra"))
            self.assertEqual(record.extra["service"], "test_service")
            self.assertEqual(record.extra["key"], "value")
    
    def test_json_formatter_with_service_context(self):
        """Test that JsonFormatter includes service context in the formatted record."""
        # Create a formatter
        formatter = JsonFormatter()
        
        # Create a log record
        record = logging.LogRecord(
            name="test_service.test_module",
            level=logging.INFO,
            pathname="test_path",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add service context
        record.extra = {"service": "test_service", "key": "value"}
        
        # Format the record
        formatted = formatter.format(record)
        
        # Check that the result is valid JSON
        log_data = json.loads(formatted)
        
        # Check that service context is included
        self.assertEqual(log_data["service"], "test_service")
        self.assertEqual(log_data["key"], "value")

if __name__ == "__main__":
    unittest.main()
