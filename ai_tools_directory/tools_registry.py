"""AI Tools Registry Module

This module provides a registry for AI tools and services that can be integrated
with the real estate AI bot. It follows the microservice principles of service
orchestration and plugin-based architecture.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional, Union, Callable
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ai_tools_registry')

class AIToolsRegistry:
    """Registry for AI tools and services."""
    
    def __init__(self, registry_file: Optional[str] = None):
        """Initialize the AI tools registry.
        
        Args:
            registry_file: Path to the registry file (optional)
        """
        self.logger = logging.getLogger('ai_tools_registry')
        
        # Set the registry file path
        if registry_file:
            self.registry_file = registry_file
        else:
            self.registry_file = os.path.join(os.path.dirname(__file__), 'tools_registry.json')
        
        # Initialize the registry
        self.registry = {}
        
        # Load the registry if it exists
        self._load_registry()
    
    def _load_registry(self):
        """Load the registry from the registry file."""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self.registry = json.load(f)
                self.logger.info(f"Loaded {len(self.registry)} tools from registry")
            except Exception as e:
                self.logger.error(f"Error loading registry: {str(e)}")
                self.registry = {}
        else:
            self.logger.info("Registry file does not exist, creating a new registry")
            self.registry = {}
            self._save_registry()
    
    def _save_registry(self):
        """Save the registry to the registry file."""
        try:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2)
            self.logger.info(f"Saved {len(self.registry)} tools to registry")
        except Exception as e:
            self.logger.error(f"Error saving registry: {str(e)}")
    
    def register_tool(self, tool_id: str, tool_data: Dict[str, Any]) -> bool:
        """Register a new AI tool or update an existing one.
        
        Args:
            tool_id: Unique identifier for the tool
            tool_data: Data about the tool
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add or update the tool in the registry
            self.registry[tool_id] = {
                **tool_data,
                "last_updated": datetime.now().isoformat()
            }
            
            # Save the registry
            self._save_registry()
            
            self.logger.info(f"Registered tool: {tool_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error registering tool {tool_id}: {str(e)}")
            return False
    
    def unregister_tool(self, tool_id: str) -> bool:
        """Unregister an AI tool.
        
        Args:
            tool_id: Unique identifier for the tool
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Remove the tool from the registry
            if tool_id in self.registry:
                del self.registry[tool_id]
                
                # Save the registry
                self._save_registry()
                
                self.logger.info(f"Unregistered tool: {tool_id}")
                return True
            else:
                self.logger.warning(f"Tool not found in registry: {tool_id}")
                return False
        except Exception as e:
            self.logger.error(f"Error unregistering tool {tool_id}: {str(e)}")
            return False
    
    def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get information about an AI tool.
        
        Args:
            tool_id: Unique identifier for the tool
            
        Returns:
            Tool data dictionary or None if not found
        """
        return self.registry.get(tool_id)
    
    def get_all_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered AI tools.
        
        Returns:
            Dictionary of all registered tools
        """
        return self.registry
    
    def get_tools_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get all AI tools in a specific category.
        
        Args:
            category: Category of tools to get
            
        Returns:
            Dictionary of tools in the specified category
        """
        return {tool_id: tool_data for tool_id, tool_data in self.registry.items()
                if tool_data.get("category") == category}
    
    def get_tools_by_tag(self, tag: str) -> Dict[str, Dict[str, Any]]:
        """Get all AI tools with a specific tag.
        
        Args:
            tag: Tag to search for
            
        Returns:
            Dictionary of tools with the specified tag
        """
        return {tool_id: tool_data for tool_id, tool_data in self.registry.items()
                if tag in tool_data.get("tags", [])}
    
    def search_tools(self, query: str) -> Dict[str, Dict[str, Any]]:
        """Search for AI tools by name, description, or tags.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary of matching tools
        """
        query = query.lower()
        return {tool_id: tool_data for tool_id, tool_data in self.registry.items()
                if query in tool_data.get("name", "").lower() or
                   query in tool_data.get("description", "").lower() or
                   any(query in tag.lower() for tag in tool_data.get("tags", []))}
    
    def import_from_directory(self, directory_url: str) -> int:
        """Import tools from an online directory.
        
        Args:
            directory_url: URL of the directory to import from
            
        Returns:
            Number of tools imported
        """
        try:
            # Get the directory data
            response = requests.get(directory_url)
            response.raise_for_status()
            directory_data = response.json()
            
            # Import each tool
            imported_count = 0
            for tool_id, tool_data in directory_data.items():
                if self.register_tool(tool_id, tool_data):
                    imported_count += 1
            
            self.logger.info(f"Imported {imported_count} tools from {directory_url}")
            return imported_count
        except Exception as e:
            self.logger.error(f"Error importing from directory {directory_url}: {str(e)}")
            return 0
    
    def export_to_file(self, export_file: str) -> bool:
        """Export the registry to a file.
        
        Args:
            export_file: Path to the export file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, indent=2)
            self.logger.info(f"Exported registry to {export_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error exporting registry to {export_file}: {str(e)}")
            return False
