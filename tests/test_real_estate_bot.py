"""
Test suite for Real Estate AI Bot
Tests all major functionalities including property analysis, lead scoring, and market insights
"""
import unittest
import asyncio
from datetime import datetime
from unittest.mock import Mock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import RealEstateBot
from firebase_manager import FirebaseManager

class TestRealEstateBot(unittest.TestCase):
    """Test cases for RealEstateBot functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.bot = RealEstateBot()
        self.test_address = "123 Main St"
        self.test_zip = "12345"
        
    def tearDown(self):
        """Clean up after tests"""
        self.bot.stop()
    
    def test_property_analysis_structure(self):
        """Test property analysis response structure"""
        async def run_test():
            response = await self.bot.analyze_property(
                self.test_address,
                self.test_zip
            )
            
            # Check response structure
            self.assertIn('property_value', response)
            self.assertIn('property_details', response)
            self.assertIn('tax_assessment', response)
            self.assertIn('owner_info', response)
            
            # Check value estimates
            value_data = response['property_value']
            self.assertIn('estimated_value', value_data)
            self.assertIn('confidence_score', value_data)
            
            # Check property details
            details = response['property_details']
            self.assertIn('basic_info', details)
            self.assertIn('construction', details)
            self.assertIn('systems', details)
            
        asyncio.run(run_test())
    
    def test_market_trends_structure(self):
        """Test market trends response structure"""
        async def run_test():
            response = await self.bot.get_market_trends(self.test_zip)
            
            # Check response structure
            self.assertIn('price_trends', response)
            self.assertIn('sales_velocity', response)
            self.assertIn('inventory_levels', response)
            self.assertIn('rental_metrics', response)
            
            # Check price trends
            trends = response['price_trends']
            self.assertTrue(isinstance(trends, list))
            if trends:
                self.assertIn('period', trends[0])
                self.assertIn('change', trends[0])
            
        asyncio.run(run_test())
    
    def test_investment_analysis_structure(self):
        """Test investment analysis response structure"""
        async def run_test():
            response = await self.bot.analyze_investment(
                self.test_address,
                self.test_zip
            )
            
            # Check response structure
            self.assertIn('arv', response)
            self.assertIn('repairs', response)
            self.assertIn('mao', response)
            self.assertIn('roi', response)
            
            # Check ARV details
            arv_data = response['arv']
            self.assertIn('value', arv_data)
            self.assertIn('comps', arv_data)
            
            # Check ROI details
            roi_data = response['roi']
            self.assertIn('percentage', roi_data)
            self.assertIn('timeline', roi_data)
            
        asyncio.run(run_test())
    
    def test_lead_scoring_structure(self):
        """Test lead scoring response structure"""
        async def run_test():
            response = await self.bot.analyze_property(
                self.test_address,
                self.test_zip
            )
            
            # Check lead analysis structure
            self.assertIn('lead_analysis', response)
            lead_data = response['lead_analysis']
            
            # Check scores
            self.assertIn('scores', lead_data)
            scores = lead_data['scores']
            self.assertIn('financial_distress', scores)
            self.assertIn('property_condition', scores)
            self.assertIn('market_position', scores)
            self.assertIn('timing', scores)
            
            # Check status
            self.assertIn('status', lead_data)
            status = lead_data['status']
            self.assertIn('category', status)
            self.assertIn('priority', status)
            
        asyncio.run(run_test())
    
    def test_caching_behavior(self):
        """Test caching functionality"""
        async def run_test():
            # First request
            response1 = await self.bot.analyze_property(
                self.test_address,
                self.test_zip
            )
            
            # Second request (should be cached)
            response2 = await self.bot.analyze_property(
                self.test_address,
                self.test_zip
            )
            
            # Verify responses match
            self.assertEqual(response1, response2)
            
        asyncio.run(run_test())
    
    def test_error_handling(self):
        """Test error handling"""
        async def run_test():
            # Test with invalid ZIP code
            response = await self.bot.get_market_trends("00000")
            self.assertIn('error', response)
            
            # Test with invalid address
            response = await self.bot.analyze_property("", "12345")
            self.assertIn('error', response)
            
        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
