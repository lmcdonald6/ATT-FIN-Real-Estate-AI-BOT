import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.config.env_manager import EnvManager
from src.ai.model_provider import ModelProviderFactory, FallbackProvider
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Demo script to test AI model providers"""
    # Initialize environment manager
    env_manager = EnvManager()
    
    # Check available providers
    validation = env_manager.validate_keys()
    logger.info("Available AI Providers:")
    for provider, is_valid in validation.items():
        status = "✓ Ready" if is_valid else "✗ Not configured"
        logger.info(f"- {provider}: {status}")
    
    # Test message
    test_message = "I'm looking for investment properties in Beverly Hills under $500k"
    test_context = {
        "property_preferences": {
            "location": "Beverly Hills",
            "max_price": 500000
        }
    }
    
    # Try each available provider
    for provider_name, is_valid in validation.items():
        if is_valid:
            logger.info(f"\nTesting {provider_name.upper()} provider:")
            try:
                provider = ModelProviderFactory.create_provider(provider_name)
                
                # Test intent analysis
                logger.info("Analyzing intent...")
                intent_response = provider.analyze_intent(test_message)
                logger.info(f"Intent: {intent_response.content}")
                
                # Test response generation
                logger.info("Generating response...")
                response = provider.generate_response(test_message, test_context)
                logger.info(f"Response: {response.content}")
                logger.info(f"Model: {response.model}")
                if response.usage:
                    logger.info(f"Usage: {response.usage}")
                    
            except Exception as e:
                logger.error(f"Error testing {provider_name}: {str(e)}")
    
    # Test fallback provider
    logger.info("\nTesting Fallback Provider:")
    try:
        fallback = FallbackProvider()
        response = fallback.generate_response(test_message, test_context)
        logger.info(f"Selected Provider: {response.provider}")
        logger.info(f"Response: {response.content}")
        logger.info(f"Model: {response.model}")
        if response.usage:
            logger.info(f"Usage: {response.usage}")
            
    except Exception as e:
        logger.error(f"Error testing fallback provider: {str(e)}")

if __name__ == "__main__":
    main()
