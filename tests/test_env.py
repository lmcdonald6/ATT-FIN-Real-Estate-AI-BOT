import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import unittest
from src.config.env_manager import EnvManager
import tempfile
import json

class TestEnvManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_app_name = "TEST_AI"
        self.env_manager = EnvManager(self.test_app_name)
        self.test_keys = {
            'openai': 'sk-test-openai-key-123456789',
            'anthropic': 'sk-ant-test123-456789',
            'google': 'test-google-key-123456789012345678901234'
        }
        
    def test_api_key_management(self):
        """Test API key storage and retrieval"""
        # Test setting keys
        for provider, key in self.test_keys.items():
            self.assertTrue(self.env_manager.set_api_key(provider, key))
            
        # Test retrieving keys
        for provider, expected_key in self.test_keys.items():
            retrieved_key = self.env_manager.get_api_key(provider)
            self.assertEqual(retrieved_key, expected_key)
            
    def test_validation(self):
        """Test key validation"""
        # Initially no keys should be valid
        validation = self.env_manager.validate_keys()
        self.assertFalse(any(validation.values()))
        
        # Add keys and validate again
        for provider, key in self.test_keys.items():
            self.assertTrue(self.env_manager.set_api_key(provider, key))
            
        validation = self.env_manager.validate_keys()
        self.assertTrue(all(validation.values()))
        
        # Test invalid key formats
        invalid_keys = {
            'openai': 'invalid-key',
            'anthropic': 'invalid-key',
            'google': 'short'
        }
        
        for provider, key in invalid_keys.items():
            self.env_manager.set_api_key(provider, key)
            validation = self.env_manager.validate_keys()
            self.assertFalse(validation[provider])
        
    def test_config_export(self):
        """Test configuration export"""
        # Set up test keys
        for provider, key in self.test_keys.items():
            self.assertTrue(self.env_manager.set_api_key(provider, key))
            
        # Export to temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            self.assertTrue(self.env_manager.export_config(temp_file.name))
            
            # Read and verify config
            with open(temp_file.name, 'r') as f:
                config = json.load(f)
                
            self.assertEqual(set(config['available_providers']), set(self.test_keys.keys()))
            self.assertEqual(config['app_name'], self.test_app_name)
            
        # Clean up
        os.unlink(temp_file.name)
        
    def test_env_file_creation(self):
        """Test .env file creation"""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / '.env'
            
            # Create .env file
            self.assertTrue(EnvManager.create_env_file(self.test_keys, str(env_path)))
            
            # Verify file contents
            self.assertTrue(env_path.exists())
            with open(env_path, 'r') as f:
                content = f.read()
                for provider, key in self.test_keys.items():
                    self.assertIn(f'{provider.upper()}_API_KEY="{key}"', content)
                    
    def test_error_handling(self):
        """Test error handling"""
        # Test with invalid path
        self.assertFalse(self.env_manager.export_config('/invalid/path/config.json'))
        self.assertFalse(EnvManager.create_env_file({}, '/invalid/path/.env'))
        
        # Test with invalid keys
        self.assertIsNone(self.env_manager.get_api_key('invalid_provider'))
        self.assertFalse(self.env_manager.set_api_key('', ''))

if __name__ == '__main__':
    unittest.main(verbosity=2)
