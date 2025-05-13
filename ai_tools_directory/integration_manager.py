"""AI Tools Integration Manager Module

This module provides functionality to integrate AI tools and services with the
real estate AI bot. It follows the microservice principles of plugin-based
architecture and service orchestration.
"""

import os
import sys
import json
import logging
import importlib
import importlib.util
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime

# Import the tools registry
from ai_tools_directory.tools_registry import AIToolsRegistry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('integration_manager')

class ToolIntegrationManager:
    """Manager for integrating AI tools and services."""
    
    def __init__(self, registry: Optional[AIToolsRegistry] = None):
        """Initialize the tool integration manager.
        
        Args:
            registry: AI tools registry (optional)
        """
        self.logger = logging.getLogger('integration_manager')
        
        # Set the registry
        if registry:
            self.registry = registry
        else:
            self.registry = AIToolsRegistry()
        
        # Initialize the integrations directory
        self.integrations_dir = os.path.join(os.path.dirname(__file__), 'integrations')
        os.makedirs(self.integrations_dir, exist_ok=True)
        
        # Initialize the integrated tools
        self.integrated_tools = {}
        
        # Load all integrations
        self._load_integrations()
    
    def _load_integrations(self):
        """Load all integrations from the integrations directory."""
        # Check if the integrations directory exists
        if not os.path.exists(self.integrations_dir):
            self.logger.warning(f"Integrations directory does not exist: {self.integrations_dir}")
            return
        
        # Get all Python files in the integrations directory
        integration_files = [f for f in os.listdir(self.integrations_dir) 
                            if f.endswith('.py') and not f.startswith('__')]
        
        # Load each integration
        for file in integration_files:
            try:
                # Get the module name
                module_name = file[:-3]  # Remove the .py extension
                
                # Load the module
                module_path = os.path.join(self.integrations_dir, file)
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Check if the module has an integration class
                if hasattr(module, 'ToolIntegration'):
                    # Create an instance of the integration class
                    integration = module.ToolIntegration()
                    
                    # Add the integration to the integrated tools
                    self.integrated_tools[module_name] = {
                        'module': module,
                        'integration': integration,
                        'info': integration.get_info() if hasattr(integration, 'get_info') else {}
                    }
                    
                    self.logger.info(f"Loaded integration: {module_name}")
                else:
                    self.logger.warning(f"No ToolIntegration class found in {file}")
            except Exception as e:
                self.logger.error(f"Error loading integration {file}: {str(e)}")
    
    def get_integrated_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all integrated tools.
        
        Returns:
            Dictionary of integrated tools
        """
        return {tool_id: tool_data['info'] for tool_id, tool_data in self.integrated_tools.items()}
    
    def get_integration(self, tool_id: str) -> Optional[Any]:
        """Get an integration by its ID.
        
        Args:
            tool_id: ID of the integration to get
            
        Returns:
            Integration object or None if not found
        """
        if tool_id in self.integrated_tools:
            return self.integrated_tools[tool_id]['integration']
        return None
    
    def integrate_tool(self, tool_id: str) -> bool:
        """Integrate a tool from the registry.
        
        Args:
            tool_id: ID of the tool to integrate
            
        Returns:
            True if successful, False otherwise
        """
        # Check if the tool exists in the registry
        tool_data = self.registry.get_tool(tool_id)
        if not tool_data:
            self.logger.error(f"Tool not found in registry: {tool_id}")
            return False
        
        # Check if the tool is already integrated
        if tool_id in self.integrated_tools:
            self.logger.warning(f"Tool already integrated: {tool_id}")
            return True
        
        try:
            # Get the integration code
            integration_code = tool_data.get('integration_code')
            if not integration_code:
                self.logger.error(f"No integration code found for tool: {tool_id}")
                return False
            
            # Create the integration file
            integration_file = os.path.join(self.integrations_dir, f"{tool_id}.py")
            with open(integration_file, 'w', encoding='utf-8') as f:
                f.write(integration_code)
            
            # Load the integration
            spec = importlib.util.spec_from_file_location(tool_id, integration_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if the module has an integration class
            if hasattr(module, 'ToolIntegration'):
                # Create an instance of the integration class
                integration = module.ToolIntegration()
                
                # Add the integration to the integrated tools
                self.integrated_tools[tool_id] = {
                    'module': module,
                    'integration': integration,
                    'info': integration.get_info() if hasattr(integration, 'get_info') else {}
                }
                
                self.logger.info(f"Integrated tool: {tool_id}")
                return True
            else:
                self.logger.error(f"No ToolIntegration class found in {tool_id}.py")
                return False
        except Exception as e:
            self.logger.error(f"Error integrating tool {tool_id}: {str(e)}")
            return False
    
    def remove_integration(self, tool_id: str) -> bool:
        """Remove an integration.
        
        Args:
            tool_id: ID of the integration to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if the tool is integrated
            if tool_id not in self.integrated_tools:
                self.logger.warning(f"Tool not integrated: {tool_id}")
                return False
            
            # Remove the integration from the integrated tools
            del self.integrated_tools[tool_id]
            
            # Remove the integration file
            integration_file = os.path.join(self.integrations_dir, f"{tool_id}.py")
            if os.path.exists(integration_file):
                os.remove(integration_file)
            
            self.logger.info(f"Removed integration: {tool_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error removing integration {tool_id}: {str(e)}")
            return False
    
    def call_tool_method(self, tool_id: str, method_name: str, *args, **kwargs) -> Any:
        """Call a method on an integrated tool.
        
        Args:
            tool_id: ID of the tool to call
            method_name: Name of the method to call
            *args: Positional arguments to pass to the method
            **kwargs: Keyword arguments to pass to the method
            
        Returns:
            Result of the method call
        """
        # Get the integration
        integration = self.get_integration(tool_id)
        if not integration:
            self.logger.error(f"Tool not integrated: {tool_id}")
            return None
        
        # Check if the method exists
        if not hasattr(integration, method_name):
            self.logger.error(f"Method not found on tool {tool_id}: {method_name}")
            return None
        
        try:
            # Call the method
            method = getattr(integration, method_name)
            result = method(*args, **kwargs)
            
            self.logger.info(f"Called method {method_name} on tool {tool_id}")
            return result
        except Exception as e:
            self.logger.error(f"Error calling method {method_name} on tool {tool_id}: {str(e)}")
            return None
    
    def discover_tools(self, directory_url: str) -> List[Dict[str, Any]]:
        """Discover new tools from a directory.
        
        Args:
            directory_url: URL of the directory to discover tools from
            
        Returns:
            List of discovered tools
        """
        # Import tools from the directory
        imported_count = self.registry.import_from_directory(directory_url)
        
        # Get all tools that are not already integrated
        all_tools = self.registry.get_all_tools()
        integrated_tool_ids = set(self.integrated_tools.keys())
        
        discovered_tools = []
        for tool_id, tool_data in all_tools.items():
            if tool_id not in integrated_tool_ids:
                discovered_tools.append({
                    'id': tool_id,
                    **tool_data
                })
        
        self.logger.info(f"Discovered {len(discovered_tools)} new tools")
        return discovered_tools
