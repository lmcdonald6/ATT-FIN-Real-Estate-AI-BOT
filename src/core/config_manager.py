"""
Configuration manager for AI system customization.
Handles loading, validation, and hot-reloading of configurations.
"""
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

class ConfigChangeHandler(FileSystemEventHandler):
    """Handles configuration file changes"""
    
    def __init__(self, config_manager: 'ConfigManager'):
        self.config_manager = config_manager
        
    def on_modified(self, event):
        if event.src_path.endswith(('.yaml', '.yml', '.json')):
            self.config_manager.reload_config(event.src_path)

class ConfigManager:
    """Manages system configuration and customization"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.configs: Dict[str, Dict] = {}
        self.schemas: Dict[str, Dict] = {}
        self.observers: Dict[str, Set[callable]] = {}
        self.file_observer = Observer()
        
        # Initialize configuration directory
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Start file watching
        event_handler = ConfigChangeHandler(self)
        self.file_observer.schedule(event_handler, str(self.config_dir), recursive=True)
        self.file_observer.start()
        
    def load_config(self, name: str) -> Optional[Dict]:
        """Load configuration by name"""
        try:
            # Check for YAML config
            yaml_path = self.config_dir / f"{name}.yaml"
            if yaml_path.exists():
                with open(yaml_path) as f:
                    config = yaml.safe_load(f)
                    
            # Check for JSON config
            else:
                json_path = self.config_dir / f"{name}.json"
                if not json_path.exists():
                    logger.error(f"No configuration file found for: {name}")
                    return None
                    
                with open(json_path) as f:
                    config = json.load(f)
                    
            # Validate against schema if exists
            if name in self.schemas:
                if not self._validate_config(config, self.schemas[name]):
                    logger.error(f"Invalid configuration for: {name}")
                    return None
                    
            self.configs[name] = config
            return config
            
        except Exception as e:
            logger.error(f"Error loading config {name}: {str(e)}")
            return None
            
    def save_config(self, name: str, config: Dict) -> bool:
        """Save configuration to file"""
        try:
            # Validate against schema if exists
            if name in self.schemas:
                if not self._validate_config(config, self.schemas[name]):
                    logger.error(f"Invalid configuration for: {name}")
                    return False
                    
            # Save as YAML if exists, otherwise JSON
            yaml_path = self.config_dir / f"{name}.yaml"
            if yaml_path.exists():
                with open(yaml_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
            else:
                json_path = self.config_dir / f"{name}.json"
                with open(json_path, 'w') as f:
                    json.dump(config, f, indent=2)
                    
            self.configs[name] = config
            return True
            
        except Exception as e:
            logger.error(f"Error saving config {name}: {str(e)}")
            return False
            
    def register_schema(self, name: str, schema: Dict) -> bool:
        """Register JSON schema for configuration validation"""
        try:
            # TODO: Validate schema format
            self.schemas[name] = schema
            return True
        except Exception as e:
            logger.error(f"Error registering schema for {name}: {str(e)}")
            return False
            
    def get_config(self, name: str, default: Dict = None) -> Dict:
        """Get configuration by name"""
        if name not in self.configs:
            self.load_config(name)
        return self.configs.get(name, default or {})
        
    def update_config(self, name: str, updates: Dict) -> bool:
        """Update configuration with new values"""
        current = self.get_config(name, {})
        updated = self._deep_update(current, updates)
        return self.save_config(name, updated)
        
    def subscribe_to_changes(self, name: str, callback: callable) -> bool:
        """Subscribe to configuration changes"""
        if name not in self.observers:
            self.observers[name] = set()
        self.observers[name].add(callback)
        return True
        
    def unsubscribe_from_changes(self, name: str, callback: callable) -> bool:
        """Unsubscribe from configuration changes"""
        if name in self.observers:
            self.observers[name].discard(callback)
            return True
        return False
        
    def reload_config(self, file_path: str):
        """Reload configuration from file"""
        name = Path(file_path).stem
        if self.load_config(name):
            self._notify_observers(name)
            
    def _notify_observers(self, name: str):
        """Notify observers of configuration changes"""
        if name in self.observers:
            config = self.get_config(name)
            for callback in self.observers[name]:
                try:
                    callback(config)
                except Exception as e:
                    logger.error(f"Error in config observer callback: {str(e)}")
                    
    def _validate_config(self, config: Dict, schema: Dict) -> bool:
        """Validate configuration against JSON schema"""
        # TODO: Implement JSON schema validation
        return True
        
    def _deep_update(self, base: Dict, updates: Dict) -> Dict:
        """Deep update dictionary"""
        for key, value in updates.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                base[key] = self._deep_update(base[key], value)
            else:
                base[key] = value
        return base
        
    def cleanup(self):
        """Cleanup resources"""
        self.file_observer.stop()
        self.file_observer.join()
