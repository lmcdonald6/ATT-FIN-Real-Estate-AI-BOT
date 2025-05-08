import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.config.env_manager import EnvManager

def setup_environment():
    """Interactive script to set up API keys and environment variables"""
    print("Real Estate AI System - Environment Setup")
    print("----------------------------------------")
    
    env_manager = EnvManager()
    
    # Get API keys from user
    providers = {
        'openai': 'OpenAI',
        'anthropic': 'Anthropic (Claude)',
        'google': 'Google (Gemini)'
    }
    
    api_keys = {}
    for key, name in providers.items():
        existing_key = env_manager.get_api_key(key)
        if existing_key:
            print(f"\n{name} API key already exists.")
            update = input(f"Would you like to update the {name} API key? (y/n): ").lower()
            if update == 'y':
                new_key = input(f"Enter new {name} API key: ").strip()
                if new_key:
                    api_keys[key] = new_key
        else:
            print(f"\n{name} API key not found.")
            new_key = input(f"Enter {name} API key (press Enter to skip): ").strip()
            if new_key:
                api_keys[key] = new_key
    
    # Save API keys
    if api_keys:
        # Create .env file
        EnvManager.create_env_file(api_keys)
        
        # Store in keyring
        for provider, key in api_keys.items():
            env_manager.set_api_key(provider, key)
            
        print("\nAPI keys have been saved securely.")
    
    # Validate configuration
    print("\nValidating configuration...")
    validation = env_manager.validate_keys()
    
    print("\nAvailable AI Providers:")
    for provider, is_valid in validation.items():
        status = "✓ Ready" if is_valid else "✗ Not configured"
        print(f"- {providers[provider]}: {status}")
    
    # Export configuration
    env_manager.export_config()
    print("\nConfiguration has been exported to config.json")
    
    if not any(validation.values()):
        print("\nWarning: No AI providers are configured. At least one provider is required.")
        return False
    
    return True

if __name__ == "__main__":
    if setup_environment():
        print("\nSetup completed successfully!")
    else:
        print("\nSetup incomplete. Please configure at least one AI provider.")
