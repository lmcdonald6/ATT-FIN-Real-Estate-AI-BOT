"""
API endpoints for plugin management.
"""
import logging
from pathlib import Path
from typing import Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.core.config_manager import ConfigManager
from src.core.plugin_system import PluginManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/plugins")

# Initialize managers
config_manager = ConfigManager()
plugin_manager = PluginManager()

class PluginConfig(BaseModel):
    """Plugin configuration model"""
    config: Dict

class PluginInfo(BaseModel):
    """Plugin information model"""
    name: str
    version: str
    description: str
    author: str
    enabled: bool
    capabilities: List[str]
    config: Dict

@router.get("/", response_model=List[PluginInfo])
async def list_plugins():
    """Get list of all plugins"""
    try:
        plugins = []
        for plugin in plugin_manager.get_plugins():
            config = config_manager.get_config(plugin.name)
            plugins.append(PluginInfo(
                name=plugin.name,
                version=plugin.version,
                description=plugin.description,
                author=plugin.author,
                enabled=plugin.enabled,
                capabilities=plugin.get_capabilities(),
                config=config
            ))
        return plugins
    except Exception as e:
        logger.error(f"Error listing plugins: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list plugins")

@router.post("/{plugin_name}/toggle")
async def toggle_plugin(plugin_name: str):
    """Toggle plugin enabled state"""
    try:
        plugin = plugin_manager.get_plugin(plugin_name)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")
            
        success = plugin_manager.toggle_plugin(plugin_name)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to toggle plugin")
            
        return {"status": "success", "enabled": plugin.enabled}
    except Exception as e:
        logger.error(f"Error toggling plugin {plugin_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to toggle plugin")

@router.get("/{plugin_name}/config")
async def get_plugin_config(plugin_name: str):
    """Get plugin configuration"""
    try:
        plugin = plugin_manager.get_plugin(plugin_name)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")
            
        config = config_manager.get_config(plugin_name)
        return config
    except Exception as e:
        logger.error(f"Error getting config for {plugin_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get plugin config")

@router.post("/{plugin_name}/config")
async def update_plugin_config(plugin_name: str, config: PluginConfig):
    """Update plugin configuration"""
    try:
        plugin = plugin_manager.get_plugin(plugin_name)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")
            
        success = config_manager.update_config(plugin_name, config.config)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update config")
            
        # Reinitialize plugin with new config
        plugin.initialize(config.config)
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error updating config for {plugin_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update plugin config")

@router.get("/{plugin_name}/schema")
async def get_plugin_schema(plugin_name: str):
    """Get plugin configuration schema"""
    try:
        plugin = plugin_manager.get_plugin(plugin_name)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")
            
        schema = plugin.get_config_schema()
        return schema
    except Exception as e:
        logger.error(f"Error getting schema for {plugin_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get plugin schema")
