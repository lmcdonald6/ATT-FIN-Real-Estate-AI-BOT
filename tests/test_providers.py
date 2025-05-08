import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import unittest
from src.ai.model_provider import ModelProviderFactory, FallbackProvider
from src.config.env_manager import EnvManager

class TestAIProviders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.env_manager = EnvManager()
        cls.test_message = "I'm looking for investment properties in Beverly Hills under $500k"
        cls.test_context = {
            "property_preferences": {
                "location": "Beverly Hills",
                "max_price": 500000
            }
        }
    
    def test_individual_providers(self):
        """Test each available provider individually"""
        for provider_name in ['openai', 'anthropic', 'google']:
            if self.env_manager.get_api_key(provider_name):
                with self.subTest(provider=provider_name):
                    provider = ModelProviderFactory.create_provider(provider_name)
                    
                    # Test intent analysis
                    intent_response = provider.analyze_intent(self.test_message)
                    self.assertIsNotNone(intent_response.content)
                    self.assertEqual(intent_response.provider, provider_name)
                    
                    # Test response generation
                    response = provider.generate_response(self.test_message, self.test_context)
                    self.assertIsNotNone(response.content)
                    self.assertEqual(response.provider, provider_name)
                    
                    print(f"\n{provider_name.upper()} Results:")
                    print(f"Intent: {intent_response.content}")
                    print(f"Response: {response.content}")
    
    def test_fallback_provider(self):
        """Test fallback provider functionality"""
        fallback = FallbackProvider()
        
        # Test intent analysis
        intent_response = fallback.analyze_intent(self.test_message)
        self.assertIsNotNone(intent_response.content)
        
        # Test response generation
        response = fallback.generate_response(self.test_message, self.test_context)
        self.assertIsNotNone(response.content)
        
        print("\nFallback Provider Results:")
        print(f"Intent: {intent_response.content}")
        print(f"Response: {response.content}")
        print(f"Selected Provider: {response.provider}")
    
    def test_error_handling(self):
        """Test error handling with invalid API keys"""
        with self.assertRaises(ValueError):
            ModelProviderFactory.create_provider('openai', api_key='invalid_key')
    
    def test_provider_selection(self):
        """Test provider selection logic"""
        # Get available providers
        available = [p for p in ['openai', 'anthropic', 'google'] 
                    if self.env_manager.get_api_key(p)]
        
        if available:
            # Test each available provider
            for provider_name in available:
                with self.subTest(provider=provider_name):
                    provider = ModelProviderFactory.create_provider(provider_name)
                    response = provider.generate_response(self.test_message, self.test_context)
                    self.assertEqual(response.provider, provider_name)
        else:
            self.skipTest("No AI providers configured")

if __name__ == '__main__':
    unittest.main(verbosity=2)
