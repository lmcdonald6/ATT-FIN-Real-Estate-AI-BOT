"""Base Integration Class

This module provides a base class for all tool integrations.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseIntegration(ABC):
    """Base class for all tool integrations."""
    
    def __init__(self):
        """Initialize the base integration."""
        self.logger = logging.getLogger(f"integration.{self.__class__.__name__}")
    
    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """Get information about the integration.
        
        Returns:
            Dictionary of integration information
        """
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the integration with configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test the connection to the tool.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def save_config(self, config: Dict[str, Any], config_file: Optional[str] = None) -> bool:
        """Save the configuration to a file.
        
        Args:
            config: Configuration dictionary
            config_file: Path to the configuration file (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Set the configuration file path
            if not config_file:
                config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs')
                os.makedirs(config_dir, exist_ok=True)
                config_file = os.path.join(config_dir, f"{self.__class__.__name__}.json")
            
            # Save the configuration
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            self.logger.info(f"Saved configuration to {config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load the configuration from a file.
        
        Args:
            config_file: Path to the configuration file (optional)
            
        Returns:
            Configuration dictionary
        """
        try:
            # Set the configuration file path
            if not config_file:
                config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'configs')
                config_file = os.path.join(config_dir, f"{self.__class__.__name__}.json")
            
            # Check if the configuration file exists
            if not os.path.exists(config_file):
                self.logger.warning(f"Configuration file does not exist: {config_file}")
                return {}
            
            # Load the configuration
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.logger.info(f"Loaded configuration from {config_file}")
            return config
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            return {}
