"""
Plugin system for extending AI agent capabilities.
Allows businesses to add custom data sources, models, and processing logic.
"""
from abc import ABC, abstractmethod
import importlib
import inspect
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type
import yaml

logger = logging.getLogger(__name__)

class PluginMetadata:
    """Metadata for a plugin"""
    def __init__(self, data: Dict):
        self.name = data['name']
        self.version = data['version']
        self.description = data.get('description', '')
        self.author = data.get('author', '')
        self.dependencies = data.get('dependencies', [])
        self.config_schema = data.get('config_schema', {})
        self.capabilities = data.get('capabilities', [])
        self.data_sources = data.get('data_sources', [])

class Plugin(ABC):
    """Base class for all plugins"""
    
    @abstractmethod
    def initialize(self, config: Dict) -> bool:
        """Initialize the plugin with given configuration"""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Get list of plugin capabilities"""
        pass
        
    @abstractmethod
    def process(self, data: Dict) -> Dict:
        """Process data using the plugin"""
        pass

class DataSourcePlugin(Plugin):
    """Base class for data source plugins"""
    
    @abstractmethod
    async def fetch_data(self, query: Dict) -> Dict:
        """Fetch data from the source"""
        pass
        
    @abstractmethod
    def validate_data(self, data: Dict) -> bool:
        """Validate data format"""
        pass

class ModelPlugin(Plugin):
    """Base class for AI model plugins"""
    
    @abstractmethod
    async def predict(self, data: Dict) -> Dict:
        """Make predictions using the model"""
        pass
        
    @abstractmethod
    def get_model_info(self) -> Dict:
        """Get information about the model"""
        pass

class ProcessorPlugin(Plugin):
    """Base class for data processor plugins"""
    
    @abstractmethod
    async def process_data(self, data: Dict) -> Dict:
        """Process data using custom logic"""
        pass

class PluginManager:
    """Manages plugin lifecycle and configuration"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_configs: Dict[str, Dict] = {}
        self.metadata: Dict[str, PluginMetadata] = {}
        
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a plugin by name"""
        try:
            # Load plugin metadata
            metadata_path = self.plugin_dir / plugin_name / "metadata.yaml"
            if not metadata_path.exists():
                logger.error(f"No metadata found for plugin: {plugin_name}")
                return False
                
            with open(metadata_path) as f:
                metadata = yaml.safe_load(f)
                self.metadata[plugin_name] = PluginMetadata(metadata)
                
            # Load plugin configuration
            config_path = self.plugin_dir / plugin_name / "config.json"
            if config_path.exists():
                with open(config_path) as f:
                    self.plugin_configs[plugin_name] = json.load(f)
                    
            # Import plugin module
            spec = importlib.util.spec_from_file_location(
                plugin_name,
                str(self.plugin_dir / plugin_name / "plugin.py")
            )
            if not spec or not spec.loader:
                raise ImportError(f"Could not load plugin: {plugin_name}")
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin class
            plugin_class = None
            for item in dir(module):
                obj = getattr(module, item)
                if (inspect.isclass(obj) and 
                    issubclass(obj, Plugin) and 
                    obj != Plugin and
                    obj not in {DataSourcePlugin, ModelPlugin, ProcessorPlugin}):
                    plugin_class = obj
                    break
                    
            if not plugin_class:
                raise ValueError(f"No plugin class found in {plugin_name}")
                
            # Initialize plugin
            plugin = plugin_class()
            if not plugin.initialize(self.plugin_configs.get(plugin_name, {})):
                raise ValueError(f"Failed to initialize plugin: {plugin_name}")
                
            self.plugins[plugin_name] = plugin
            logger.info(f"Successfully loaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_name}: {str(e)}")
            return False
            
    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get a loaded plugin by name"""
        return self.plugins.get(plugin_name)
        
    def get_plugin_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """Get plugin metadata"""
        return self.metadata.get(plugin_name)
        
    def update_plugin_config(self, plugin_name: str, config: Dict) -> bool:
        """Update plugin configuration"""
        if plugin_name not in self.plugins:
            return False
            
        try:
            # Validate against schema
            metadata = self.metadata[plugin_name]
            if metadata.config_schema:
                # TODO: Add JSON schema validation
                pass
                
            # Save configuration
            config_path = self.plugin_dir / plugin_name / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            # Reinitialize plugin
            self.plugin_configs[plugin_name] = config
            return self.plugins[plugin_name].initialize(config)
            
        except Exception as e:
            logger.error(f"Error updating config for {plugin_name}: {str(e)}")
            return False
            
    def get_available_plugins(self) -> List[str]:
        """Get list of available plugins"""
        return [p.name for p in self.plugin_dir.iterdir() 
                if p.is_dir() and (p / "metadata.yaml").exists()]
                
    def get_plugin_capabilities(self, plugin_name: str) -> List[str]:
        """Get capabilities of a plugin"""
        plugin = self.plugins.get(plugin_name)
        return plugin.get_capabilities() if plugin else []
