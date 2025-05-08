import os
from pathlib import Path
from typing import Dict, Optional
from dotenv import load_dotenv
import keyring
import json
import logging

logger = logging.getLogger(__name__)

class EnvManager:
    """Secure environment variable manager with keyring integration"""
    
    def __init__(self, app_name: str = "WHOLESALE_AI"):
        self.app_name = app_name
        self._load_env()
        self._clear_test_keys()  # Clear any test keys from previous test runs
        
    def _load_env(self) -> None:
        """Load environment variables from .env file"""
        try:
            env_path = Path(__file__).parent.parent.parent / '.env'
            load_dotenv(env_path)
        except Exception as e:
            logger.warning(f"Failed to load .env file: {str(e)}")
            
    def _clear_test_keys(self) -> None:
        """Clear test API keys from keyring"""
        if self.app_name.startswith("TEST_"):
            providers = ['openai', 'anthropic', 'google']
            for provider in providers:
                try:
                    keyring.delete_password(self.app_name, f"{provider.upper()}_API_KEY")
                except keyring.errors.PasswordDeleteError:
                    pass
        
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider, first checking keyring then env vars"""
        try:
            # Try to get from keyring first
            key = keyring.get_password(self.app_name, f"{provider.upper()}_API_KEY")
            if key:
                return key
                
            # Fall back to environment variable
            env_key = os.getenv(f"{provider.upper()}_API_KEY")
            if env_key:
                # Store in keyring for future use
                self.set_api_key(provider, env_key)
                return env_key
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting API key for {provider}: {str(e)}")
            return None
        
    def set_api_key(self, provider: str, api_key: str) -> bool:
        """Securely store API key in keyring"""
        try:
            if not provider or not api_key:
                return False
            keyring.set_password(self.app_name, f"{provider.upper()}_API_KEY", api_key)
            return True
        except Exception as e:
            logger.error(f"Error setting API key for {provider}: {str(e)}")
            return False
        
    def get_all_keys(self) -> Dict[str, Optional[str]]:
        """Get all available API keys"""
        providers = ['openai', 'anthropic', 'google']
        return {provider: self.get_api_key(provider) for provider in providers}
        
    def validate_keys(self) -> Dict[str, bool]:
        """Validate all API keys"""
        keys = self.get_all_keys()
        validations = {}
        
        for provider, key in keys.items():
            if not key:
                validations[provider] = False
                continue
                
            # Basic validation of key format
            if provider == 'openai' and not key.startswith('sk-'):
                validations[provider] = False
            elif provider == 'anthropic' and not key.startswith('sk-ant-'):
                validations[provider] = False
            elif provider == 'google' and len(key) < 20:
                validations[provider] = False
            else:
                validations[provider] = True
                
        return validations
        
    def export_config(self, path: Optional[str] = None) -> bool:
        """Export configuration (excluding sensitive data)"""
        try:
            if not path:
                path = Path(__file__).parent.parent.parent / 'config.json'
                
            config = {
                'available_providers': list(self.validate_keys().keys()),
                'active_providers': [k for k, v in self.validate_keys().items() if v],
                'app_name': self.app_name
            }
            
            with open(path, 'w') as f:
                json.dump(config, f, indent=2)
                
            return True
            
        except Exception as e:
            logger.error(f"Error exporting config: {str(e)}")
            return False
            
    @classmethod
    def create_env_file(cls, api_keys: Dict[str, str], path: Optional[str] = None) -> bool:
        """Create a .env file with API keys"""
        try:
            if not path:
                path = Path(__file__).parent.parent.parent / '.env'
                
            with open(path, 'w') as f:
                for provider, key in api_keys.items():
                    f.write(f'{provider.upper()}_API_KEY="{key}"\n')
                    
            return True
            
        except Exception as e:
            logger.error(f"Error creating .env file: {str(e)}")
            return False
