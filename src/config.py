import os
from functools import lru_cache
from typing import Dict, Optional
import yaml
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # API Settings
    api_version: str = "v1"
    debug: bool = False
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    db_pool_size: int = 5
    db_max_overflow: int = 10
    
    # Redis
    redis_url: str = Field(..., env="REDIS_URL")
    redis_pool_size: int = 10
    
    # API Keys and External Services
    zillow_api_key: Optional[str] = None
    google_maps_key: Optional[str] = None
    census_api_key: Optional[str] = None
    
    # ML Model Settings
    model_path: str = "models"
    confidence_threshold: float = 0.85
    
    # Cache Settings
    cache_ttl: int = 3600
    market_data_ttl: int = 86400
    
    # Metrics
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"

class ServiceConfig:
    def __init__(self, config_path: str = "config"):
        self.config_path = config_path
        self._config = {}
        self._load_config()
        
    def _load_config(self):
        """Load configuration from YAML files."""
        # Load base config
        base_config = os.path.join(self.config_path, "local.yaml")
        if os.path.exists(base_config):
            with open(base_config) as f:
                self._config.update(yaml.safe_load(f))
                
        # Load API config
        api_config = os.path.join(self.config_path, "api_config.yaml")
        if os.path.exists(api_config):
            with open(api_config) as f:
                self._config["apis"] = yaml.safe_load(f)
    
    def get(self, key: str, default: any = None) -> any:
        """Get configuration value by key."""
        return self._config.get(key, default)
        
    def get_service_config(self, service_name: str) -> Dict:
        """Get service-specific configuration."""
        return self._config.get(service_name, {})
        
    @property
    def api_config(self) -> Dict:
        """Get API configuration."""
        return self._config.get("apis", {})

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

@lru_cache()
def get_service_config() -> ServiceConfig:
    """Get cached service configuration instance."""
    return ServiceConfig()
