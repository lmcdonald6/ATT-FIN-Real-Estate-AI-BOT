"""
Test suite for data integration service.
Tests data source integration, validation, and error handling.
"""
import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from requests.exceptions import RequestException
from src.services.data_integration import (
    DataSourceConfig,
    MLSDataSource,
    PublicRecordsDataSource,
    DataIntegrationService
)

class TestDataIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.mls_config = DataSourceConfig(
            api_key="test_mls_key",
            base_url="https://api.mls.test"
        )
        self.public_records_config = DataSourceConfig(
            api_key="test_pr_key",
            base_url="https://api.publicrecords.test"
        )
        
        # Sample property data
        self.sample_mls_data = {
            'property_id': '123',
            'address': {
                'street': '123 Test St',
                'city': 'Test City',
                'state': 'TS',
                'zip': '12345'
            },
            'price': 500000,
            'bedrooms': 3,
            'bathrooms': 2,
            'square_feet': 2000,
            'property_type': 'Single Family',
            'year_built': 1990,
            'lot_size': 5000,
            'features': ['Pool', 'Garage']
        }
        
        self.sample_public_records = {
            'parcel_id': 'P123',
            'address': {
                'street': '123 Test St',
                'city': 'Test City',
                'state': 'TS',
                'zip': '12345'
            },
            'assessed_value': 450000,
            'tax_year': 2024,
            'tax_amount': 5000,
            'owner_info': {
                'name': 'Test Owner',
                'type': 'Individual',
                'purchase_date': '2020-01-01',
                'purchase_price': 400000
            }
        }
        
    @patch('src.services.data_integration.requests.Session')
    def test_mls_fetch_property(self, mock_session_class):
        """Test MLS property fetch"""
        # Setup mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = self.sample_mls_data
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        
        # Create MLS source with mocked session
        mls_source = MLSDataSource(self.mls_config)
        
        # Test property fetch
        property_data = mls_source.fetch_property('123')
        
        # Verify response
        self.assertEqual(property_data['property_id'], '123')
        self.assertEqual(property_data['price'], 500000)
        self.assertEqual(len(property_data['features']), 2)
        
        # Verify session was used correctly
        mock_session.get.assert_called_once_with(
            'https://api.mls.test/properties/123'
        )
        
    @patch('src.services.data_integration.requests.Session')
    def test_public_records_fetch_property(self, mock_session_class):
        """Test public records property fetch"""
        # Setup mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = self.sample_public_records
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        
        # Create public records source with mocked session
        public_records_source = PublicRecordsDataSource(self.public_records_config)
        
        # Test property fetch
        property_data = public_records_source.fetch_property('P123')
        
        # Verify response
        self.assertEqual(property_data['parcel_id'], 'P123')
        self.assertEqual(property_data['tax_info']['assessed_value'], 450000)
        self.assertEqual(property_data['ownership']['owner_name'], 'Test Owner')
        
        # Verify session was used correctly
        mock_session.get.assert_called_once_with(
            'https://api.publicrecords.test/properties/P123'
        )
        
    def test_data_validation(self):
        """Test data validation"""
        # Create sources for validation testing
        mls_source = MLSDataSource(self.mls_config)
        public_records_source = PublicRecordsDataSource(self.public_records_config)
        
        # Test valid MLS data
        self.assertTrue(mls_source.validate_data(self.sample_mls_data))
        
        # Test invalid MLS data
        invalid_mls_data = self.sample_mls_data.copy()
        del invalid_mls_data['price']
        self.assertFalse(mls_source.validate_data(invalid_mls_data))
        
        # Test valid public records data
        self.assertTrue(public_records_source.validate_data(self.sample_public_records))
        
        # Test invalid public records data
        invalid_pr_data = self.sample_public_records.copy()
        del invalid_pr_data['assessed_value']
        self.assertFalse(public_records_source.validate_data(invalid_pr_data))
        
    @patch('src.services.data_integration.requests.Session')
    def test_integration_service(self, mock_session_class):
        """Test data integration service"""
        # Setup mock session
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Setup mock responses
        def mock_get(url):
            mock_response = Mock()
            if 'mls.test' in url:
                mock_response.json.return_value = self.sample_mls_data
            elif 'publicrecords.test' in url:
                mock_response.json.return_value = self.sample_public_records
            else:
                raise ValueError(f"Unexpected URL: {url}")
            mock_response.raise_for_status.return_value = None
            return mock_response
            
        mock_session.get.side_effect = mock_get
        
        # Create integration service with mocked sources
        service = DataIntegrationService()
        service.add_data_source('mls', MLSDataSource(self.mls_config))
        service.add_data_source('public_records', PublicRecordsDataSource(self.public_records_config))
        
        # Test getting property data from all sources
        result = service.get_property_data('123')
        
        # Verify response
        self.assertIn('mls', result['data'])
        self.assertIn('public_records', result['data'])
        self.assertEqual(len(result['errors']), 0)
        
        # Verify sessions were used correctly
        mock_session.get.assert_any_call('https://api.mls.test/properties/123')
        mock_session.get.assert_any_call('https://api.publicrecords.test/properties/123')
        
    def test_error_handling(self):
        """Test error handling"""
        service = DataIntegrationService()
        
        # Test with invalid data source
        result = service.get_property_data('123', sources=['invalid_source'])
        self.assertEqual(len(result['data']), 0)
        
        # Test with failing data source
        failing_source = Mock()
        failing_source.fetch_property.side_effect = RequestException("Test error")
        service.add_data_source('failing', failing_source)
        
        result = service.get_property_data('123', sources=['failing'])
        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(result['errors'][0]['source'], 'failing')
        
if __name__ == '__main__':
    unittest.main()
