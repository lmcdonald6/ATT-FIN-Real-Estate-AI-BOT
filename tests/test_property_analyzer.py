"""
Test suite for PropertyAnalyzer class.
Tests preprocessing, sentiment analysis, and property recommendations.
"""
import unittest
import pandas as pd
from src.ai.property_analyzer import PropertyAnalyzer

class TestPropertyAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = PropertyAnalyzer()
        self.test_properties = [
            {
                'id': '1',
                'price': 300000,
                'sqft': 2000,
                'bedrooms': 3,
                'bathrooms': 2,
                'description': 'Beautiful home with modern updates'
            },
            {
                'id': '2',
                'price': 400000,
                'sqft': 2500,
                'bedrooms': 4,
                'bathrooms': 3,
                'description': 'Spacious family home with great views'
            },
            {
                'id': '3',
                'price': 350000,
                'sqft': 2200,
                'bedrooms': 3,
                'bathrooms': 2.5,
                'description': 'Recently renovated with new appliances'
            }
        ]
        
    def test_preprocess_property_data(self):
        """Test property data preprocessing"""
        df = self.analyzer.preprocess_property_data(self.test_properties)
        
        # Check DataFrame creation
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), len(self.test_properties))
        
        # Check feature engineering
        self.assertIn('price_per_sqft', df.columns)
        
        # Check outlier detection
        self.assertIn('price_is_outlier', df.columns)
        self.assertIn('sqft_is_outlier', df.columns)
        
    def test_analyze_description_sentiment(self):
        """Test description sentiment analysis"""
        description = "Beautiful modern home with great views and recent updates"
        result = self.analyzer.analyze_description_sentiment(description)
        
        # Check result structure
        self.assertIn('key_features', result)
        self.assertIn('feature_importance', result)
        
        # Check content
        self.assertTrue(len(result['key_features']) > 0)
        self.assertEqual(len(result['key_features']), len(result['feature_importance']))
        
    def test_find_similar_properties(self):
        """Test similar properties finder"""
        target = self.test_properties[0]
        similar = self.analyzer.find_similar_properties(
            target,
            self.test_properties,
            n_similar=2
        )
        
        # Check number of similar properties
        self.assertEqual(len(similar), 2)
        
        # Check that target property is not in results
        self.assertNotIn(target, similar)
        
    def test_get_property_insights(self):
        """Test property insights generation"""
        property_data = {
            'price': 300000,
            'sqft': 2000,
            'description': 'Beautiful home',
            'location': 'Great area',
            'rent_estimate': 2000
        }
        
        insights = self.analyzer.get_property_insights(property_data)
        
        # Check insights structure
        self.assertIn('sentiment', insights)
        self.assertIn('price_analysis', insights)
        self.assertIn('location_score', insights)
        self.assertIn('investment_potential', insights)
        
    def test_error_handling(self):
        """Test error handling"""
        # Test empty properties list
        with self.assertRaises(ValueError):
            self.analyzer.preprocess_property_data([])
            
        # Test empty description
        with self.assertRaises(ValueError):
            self.analyzer.analyze_description_sentiment("")
            
        # Test missing property data
        with self.assertRaises(ValueError):
            self.analyzer.get_property_insights({})
            
        # Test invalid similar properties request
        with self.assertRaises(ValueError):
            self.analyzer.find_similar_properties({}, [])
            
if __name__ == '__main__':
    unittest.main()
