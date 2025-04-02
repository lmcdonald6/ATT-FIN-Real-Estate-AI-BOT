"""
Test suite for market analysis functionality.
Tests market analysis calculations and recommendations.
"""
import unittest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from src.analysis.market_analyzer import MarketAnalyzer

class TestMarketAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = MarketAnalyzer()
        
        # Sample property data
        self.property_data = {
            'property_id': 'test123',
            'price': 400000,
            'square_feet': 2000,
            'bedrooms': 3,
            'bathrooms': 2,
            'year_built': 1990,
            'tax_info': {
                'tax_amount': 6000
            }
        }
        
        # Generate sample comps
        self.comps = self._generate_sample_comps()
        
    def _generate_sample_comps(self) -> list:
        """Generate sample comparable properties"""
        base_price = 400000
        base_date = datetime.now() - timedelta(days=365)
        
        comps = []
        for i in range(10):
            # Vary price by ±10%
            price = base_price * (1 + np.random.uniform(-0.1, 0.1))
            
            # Generate price history
            history = []
            for j in range(4):
                date = base_date + timedelta(days=90*j)
                hist_price = price * (1 + np.random.uniform(-0.05, 0.05))
                history.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'price': hist_price,
                    'event': 'Listed'
                })
            
            comps.append({
                'property_id': f'comp{i}',
                'price': price,
                'square_feet': 2000 * (1 + np.random.uniform(-0.1, 0.1)),
                'bedrooms': 3,
                'bathrooms': 2,
                'year_built': 1990,
                'price_history': history
            })
            
        return comps
        
    def test_market_analysis(self):
        """Test complete market analysis"""
        result = self.analyzer.analyze_property(self.property_data, self.comps)
        
        # Check required fields
        self.assertIn('market_position', result)
        self.assertIn('price_trends', result)
        self.assertIn('investment_metrics', result)
        self.assertIn('recommendations', result)
        
        # Check market position
        market_pos = result['market_position']
        self.assertIn('price_percentiles', market_pos)
        self.assertIn('market_segment', market_pos)
        self.assertIn('competition_level', market_pos)
        
        # Check investment metrics
        inv_metrics = result['investment_metrics']
        self.assertIn('price_to_market_ratio', inv_metrics)
        self.assertIn('estimated_monthly_rent', inv_metrics)
        self.assertIn('monthly_cashflow', inv_metrics)
        self.assertIn('annual_roi', inv_metrics)
        self.assertIn('cap_rate', inv_metrics)
        
        # Verify recommendations
        self.assertIsInstance(result['recommendations'], list)
        if result['recommendations']:
            rec = result['recommendations'][0]
            self.assertIn('type', rec)
            self.assertIn('confidence', rec)
            self.assertIn('reason', rec)
            
    def test_market_metrics_calculation(self):
        """Test calculation of market metrics"""
        metrics = self.analyzer._extract_metrics(self.property_data, self.comps)
        
        # Check required metrics
        self.assertIn('market_avg_price', metrics)
        self.assertIn('market_median_price', metrics)
        self.assertIn('price_std', metrics)
        self.assertIn('avg_price_per_sqft', metrics)
        
        # Verify calculations
        self.assertGreater(metrics['market_avg_price'], 0)
        self.assertGreater(metrics['market_median_price'], 0)
        self.assertGreater(metrics['price_std'], 0)
        
    def test_investment_metrics_calculation(self):
        """Test calculation of investment metrics"""
        metrics = self.analyzer._extract_metrics(self.property_data, self.comps)
        inv_metrics = self.analyzer._calculate_investment_metrics(
            self.property_data,
            metrics['market_avg_price'],
            0.03  # Sample appreciation rate
        )
        
        # Check required metrics
        self.assertIn('price_to_market_ratio', inv_metrics)
        self.assertIn('estimated_monthly_rent', inv_metrics)
        self.assertIn('gross_rent_multiplier', inv_metrics)
        self.assertIn('monthly_cashflow', inv_metrics)
        self.assertIn('annual_roi', inv_metrics)
        
        # Verify calculations
        self.assertGreater(inv_metrics['estimated_monthly_rent'], 0)
        self.assertGreater(inv_metrics['annual_roi'], -100)  # ROI should be reasonable
        
    def test_price_trends_analysis(self):
        """Test price trends analysis"""
        trends = self.analyzer._analyze_price_trends(self.comps)
        
        # Check required fields
        self.assertIn('appreciation_rate', trends)
        self.assertIn('price_momentum', trends)
        self.assertIn('seasonality', trends)
        
        # Verify momentum is valid
        self.assertIn(trends['price_momentum'], 
                     ['strong_up', 'up', 'stable', 'down', 'strong_down'])
        
    def test_recommendations_generation(self):
        """Test investment recommendations generation"""
        market_position = {
            'market_segment': 'Mid Market',
            'competition_level': 'Moderate',
            'price_volatility': 'Low'
        }
        
        investment_metrics = {
            'price_to_market_ratio': 0.85,
            'monthly_cashflow': 500,
            'annual_roi': 12
        }
        
        recommendations = self.analyzer._generate_recommendations(
            self.property_data,
            market_position,
            investment_metrics
        )
        
        # Verify recommendations
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Check recommendation structure
        for rec in recommendations:
            self.assertIn('type', rec)
            self.assertIn('confidence', rec)
            self.assertIn('reason', rec)
            self.assertGreaterEqual(rec['confidence'], 0)
            self.assertLessEqual(rec['confidence'], 1)
            
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test with no comps
        result = self.analyzer.analyze_property(self.property_data, [])
        self.assertIn('market_position', result)
        self.assertIn('recommendations', result)
        
        # Test with missing price
        invalid_property = self.property_data.copy()
        del invalid_property['price']
        with self.assertRaises(Exception):
            self.analyzer.analyze_property(invalid_property, self.comps)
            
if __name__ == '__main__':
    unittest.main()
