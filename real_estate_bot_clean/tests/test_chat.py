"""
Test Suite for Real Estate AI Bot
Tests query processing and response formatting.
"""

import asyncio
import unittest
from src.chat_interface import RealEstateChatInterface

class TestRealEstateChat(unittest.TestCase):
    def setUp(self):
        self.chat = RealEstateChatInterface()

    async def test_value_analysis(self):
        """Test property value analysis query."""
        query = "what is the value of 123 Main St Bessemer?"
        response = await self.chat.process_query(query)
        
        self.assertEqual(response['status'], 'success')
        self.assertIn('Value Analysis:', response['response'][0])
        self.assertIn('Current Valuation:', response['response'][3])
        self.assertIn('Market Comparison:', response['response'][8])

    async def test_property_details(self):
        """Test property details query."""
        query = "show me property details for 456 Oak Ave"
        response = await self.chat.process_query(query)
        
        self.assertEqual(response['status'], 'success')
        self.assertIn('Property Details:', response['response'][0])
        self.assertIn('Basic Information:', response['response'][3])
        self.assertIn('Construction Details:', response['response'][9])

    async def test_owner_info(self):
        """Test owner information query."""
        query = "who owns 123 Main St?"
        response = await self.chat.process_query(query)
        
        self.assertEqual(response['status'], 'success')
        self.assertIn('Owner Analysis:', response['response'][0])
        self.assertIn('Owner Profile:', response['response'][3])
        self.assertIn('Financial Status:', response['response'][8])

    async def test_occupancy_status(self):
        """Test occupancy status query."""
        query = "is 123 Main St vacant?"
        response = await self.chat.process_query(query)
        
        self.assertEqual(response['status'], 'success')
        self.assertIn('Occupancy Analysis:', response['response'][0])
        self.assertIn('Current Status:', response['response'][3])
        self.assertIn('Risk Assessment:', response['response'][13])

    async def test_distressed_properties(self):
        """Test distressed property query."""
        query = "find distressed properties with high equity in Bessemer"
        response = await self.chat.process_query(query)
        
        self.assertEqual(response['status'], 'success')
        self.assertIn('Distressed Property Analysis', response['response'][0])
        self.assertIn('Lead Score Analysis:', response['response'][9])
        self.assertIn('Action Plan:', response['response'][30])

    async def test_market_analysis(self):
        """Test market analysis query."""
        query = "show me market trends for Bessemer"
        response = await self.chat.process_query(query)
        
        self.assertEqual(response['status'], 'success')
        self.assertIn('Market Analysis Report', response['response'][0])
        self.assertIn('Price Trends & Velocity:', response['response'][3])
        self.assertIn('Market Conditions:', response['response'][9])

    async def test_investment_analysis(self):
        """Test investment analysis query."""
        query = "what's the maximum offer for 123 Main St?"
        response = await self.chat.process_query(query)
        
        self.assertEqual(response['status'], 'success')
        self.assertIn('Investment Analysis:', response['response'][0])
        self.assertIn('Purchase Analysis:', response['response'][3])
        self.assertIn('Returns:', response['response'][18])

    async def test_lead_scoring(self):
        """Test lead scoring and prioritization."""
        query = "show me vacant properties with motivated sellers in 35020"
        response = await self.chat.process_query(query)
        
        self.assertEqual(response['status'], 'success')
        self.assertIn('Lead Score Analysis:', response['response'][9])
        self.assertIn('Priority Level:', response['response'][11])
        self.assertIn('Action Plan:', response['response'][30])

def run_tests():
    """Run all test cases."""
    print("\nTesting Real Estate Chat Interface")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRealEstateChat)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

if __name__ == '__main__':
    # Run tests asynchronously
    asyncio.run(run_tests())
