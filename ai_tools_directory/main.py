"""AI Tools Directory Main Module

This module provides a command-line interface for the AI Tools Directory.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, List, Optional

# Import the tools registry and integration manager
from ai_tools_directory.tools_registry import AIToolsRegistry
from ai_tools_directory.integration_manager import ToolIntegrationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'ai_tools_directory.log'))
    ]
)
logger = logging.getLogger('ai_tools_directory')

class AIToolsDirectory:
    """Main class for the AI Tools Directory."""
    
    def __init__(self):
        """Initialize the AI Tools Directory."""
        self.logger = logging.getLogger('ai_tools_directory')
        self.registry = AIToolsRegistry()
        self.integration_manager = ToolIntegrationManager(self.registry)
    
    def list_tools(self, category: Optional[str] = None, tag: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all tools in the registry.
        
        Args:
            category: Category to filter by (optional)
            tag: Tag to filter by (optional)
            
        Returns:
            List of tool dictionaries
        """
        if category:
            tools = self.registry.get_tools_by_category(category)
        elif tag:
            tools = self.registry.get_tools_by_tag(tag)
        else:
            tools = self.registry.get_all_tools()
        
        return [{'id': tool_id, **tool_data} for tool_id, tool_data in tools.items()]
    
    def search_tools(self, query: str) -> List[Dict[str, Any]]:
        """Search for tools in the registry.
        
        Args:
            query: Search query
            
        Returns:
            List of tool dictionaries
        """
        tools = self.registry.search_tools(query)
        return [{'id': tool_id, **tool_data} for tool_id, tool_data in tools.items()]
    
    def get_tool_details(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific tool.
        
        Args:
            tool_id: ID of the tool to get details for
            
        Returns:
            Tool details dictionary or None if not found
        """
        tool_data = self.registry.get_tool(tool_id)
        if tool_data:
            return {'id': tool_id, **tool_data}
        return None
    
    def integrate_tool(self, tool_id: str) -> bool:
        """Integrate a tool from the registry.
        
        Args:
            tool_id: ID of the tool to integrate
            
        Returns:
            True if successful, False otherwise
        """
        return self.integration_manager.integrate_tool(tool_id)
    
    def remove_integration(self, tool_id: str) -> bool:
        """Remove an integration.
        
        Args:
            tool_id: ID of the integration to remove
            
        Returns:
            True if successful, False otherwise
        """
        return self.integration_manager.remove_integration(tool_id)
    
    def list_integrations(self) -> Dict[str, Dict[str, Any]]:
        """List all integrated tools.
        
        Returns:
            Dictionary of integrated tools
        """
        return self.integration_manager.get_integrated_tools()
    
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
        return self.integration_manager.call_tool_method(tool_id, method_name, *args, **kwargs)
    
    def discover_tools(self, directory_url: str) -> List[Dict[str, Any]]:
        """Discover new tools from a directory.
        
        Args:
            directory_url: URL of the directory to discover tools from
            
        Returns:
            List of discovered tools
        """
        return self.integration_manager.discover_tools(directory_url)

# Command-line interface
def main():
    """Main entry point for the AI Tools Directory."""
    parser = argparse.ArgumentParser(description="AI Tools Directory for Real Estate AI Bot")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List tools command
    list_parser = subparsers.add_parser("list", help="List all tools in the registry")
    list_parser.add_argument("--category", type=str, help="Category to filter by")
    list_parser.add_argument("--tag", type=str, help="Tag to filter by")
    
    # Search tools command
    search_parser = subparsers.add_parser("search", help="Search for tools in the registry")
    search_parser.add_argument("query", type=str, help="Search query")
    
    # Get tool details command
    details_parser = subparsers.add_parser("details", help="Get details for a specific tool")
    details_parser.add_argument("tool_id", type=str, help="ID of the tool to get details for")
    
    # Integrate tool command
    integrate_parser = subparsers.add_parser("integrate", help="Integrate a tool from the registry")
    integrate_parser.add_argument("tool_id", type=str, help="ID of the tool to integrate")
    
    # Remove integration command
    remove_parser = subparsers.add_parser("remove", help="Remove an integration")
    remove_parser.add_argument("tool_id", type=str, help="ID of the integration to remove")
    
    # List integrations command
    list_integrations_parser = subparsers.add_parser("list-integrations", help="List all integrated tools")
    
    # Call tool method command
    call_parser = subparsers.add_parser("call", help="Call a method on an integrated tool")
    call_parser.add_argument("tool_id", type=str, help="ID of the tool to call")
    call_parser.add_argument("method", type=str, help="Name of the method to call")
    call_parser.add_argument("--args", type=str, help="JSON string of positional arguments")
    call_parser.add_argument("--kwargs", type=str, help="JSON string of keyword arguments")
    
    # Discover tools command
    discover_parser = subparsers.add_parser("discover", help="Discover new tools from a directory")
    discover_parser.add_argument("directory_url", type=str, help="URL of the directory to discover tools from")
    
    args = parser.parse_args()
    
    # Create the AI Tools Directory
    directory = AIToolsDirectory()
    
    # Run the appropriate command
    if args.command == "list":
        tools = directory.list_tools(args.category, args.tag)
        print(json.dumps(tools, indent=2))
    
    elif args.command == "search":
        tools = directory.search_tools(args.query)
        print(json.dumps(tools, indent=2))
    
    elif args.command == "details":
        tool = directory.get_tool_details(args.tool_id)
        if tool:
            print(json.dumps(tool, indent=2))
        else:
            print(f"Tool not found: {args.tool_id}")
    
    elif args.command == "integrate":
        success = directory.integrate_tool(args.tool_id)
        if success:
            print(f"Successfully integrated tool: {args.tool_id}")
        else:
            print(f"Error integrating tool: {args.tool_id}")
    
    elif args.command == "remove":
        success = directory.remove_integration(args.tool_id)
        if success:
            print(f"Successfully removed integration: {args.tool_id}")
        else:
            print(f"Error removing integration: {args.tool_id}")
    
    elif args.command == "list-integrations":
        integrations = directory.list_integrations()
        print(json.dumps(integrations, indent=2))
    
    elif args.command == "call":
        # Parse the arguments and keyword arguments
        call_args = json.loads(args.args) if args.args else []
        call_kwargs = json.loads(args.kwargs) if args.kwargs else {}
        
        # Call the method
        result = directory.call_tool_method(args.tool_id, args.method, *call_args, **call_kwargs)
        print(json.dumps(result, indent=2, default=str))
    
    elif args.command == "discover":
        tools = directory.discover_tools(args.directory_url)
        print(json.dumps(tools, indent=2))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
