"""Property Analysis Tool - MVP Version"""
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class PropertyAnalyzer:
    def __init__(self):
        # Nashville market thresholds
        self.price_per_sqft_threshold = 200  # Good investment below this
        self.roi_threshold = 0.08  # 8% minimum ROI
        self.max_price = 500000  # Max price for investment properties
        
    def analyze_property(self, property_data: Dict) -> Dict:
        """Analyze a single property for investment potential"""
        try:
            analysis = {
                'price_per_sqft': self._calculate_price_per_sqft(property_data),
                'estimated_roi': self._estimate_roi(property_data),
                'investment_score': self._calculate_investment_score(property_data),
                'analysis_date': datetime.now().isoformat()
            }
            
            analysis['is_good_investment'] = self._is_good_investment(analysis)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing property: {str(e)}")
            return {}
    
    def analyze_market(self, properties: List[Dict]) -> Dict:
        """Analyze market conditions based on property list"""
        try:
            if not properties:
                return {}
            
            # Calculate market metrics
            prices = [float(p.get('price', 0)) for p in properties if p.get('price')]
            sqft_values = [float(p.get('sqft', 0)) for p in properties if p.get('sqft')]
            
            if not prices or not sqft_values:
                return {}
            
            avg_price = sum(prices) / len(prices)
            avg_sqft = sum(sqft_values) / len(sqft_values)
            avg_price_per_sqft = avg_price / avg_sqft if avg_sqft else 0
            
            return {
                'average_price': avg_price,
                'average_sqft': avg_sqft,
                'average_price_per_sqft': avg_price_per_sqft,
                'total_properties': len(properties),
                'price_range': {
                    'min': min(prices),
                    'max': max(prices)
                },
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market: {str(e)}")
            return {}
    
    def _calculate_price_per_sqft(self, property_data: Dict) -> float:
        """Calculate price per square foot"""
        try:
            price = float(property_data.get('price', 0))
            sqft = float(property_data.get('sqft', 0))
            
            if price and sqft:
                return price / sqft
            return 0
            
        except Exception:
            return 0
    
    def _estimate_roi(self, property_data: Dict) -> float:
        """Estimate potential ROI (simple calculation for MVP)"""
        try:
            # Simple ROI calculation for MVP
            price = float(property_data.get('price', 0))
            if not price:
                return 0
            
            # Estimate rental income (very basic for MVP)
            sqft = float(property_data.get('sqft', 0))
            estimated_monthly_rent = sqft * 1.5 if sqft else price * 0.008
            annual_rent = estimated_monthly_rent * 12
            
            # Estimate expenses (basic)
            annual_expenses = price * 0.03  # 3% for maintenance, taxes, etc.
            
            # Calculate ROI
            net_income = annual_rent - annual_expenses
            roi = net_income / price
            
            return roi
            
        except Exception:
            return 0
    
    def _calculate_investment_score(self, property_data: Dict) -> int:
        """Calculate investment score (0-100)"""
        try:
            score = 0
            
            # Price per sqft score (up to 40 points)
            price_per_sqft = self._calculate_price_per_sqft(property_data)
            if price_per_sqft < self.price_per_sqft_threshold:
                score += 40
            elif price_per_sqft < self.price_per_sqft_threshold * 1.2:
                score += 20
            
            # ROI score (up to 40 points)
            roi = self._estimate_roi(property_data)
            if roi >= self.roi_threshold:
                score += 40
            elif roi >= self.roi_threshold * 0.8:
                score += 20
            
            # Price range score (up to 20 points)
            price = float(property_data.get('price', 0))
            if price and price <= self.max_price:
                score += 20
            elif price and price <= self.max_price * 1.2:
                score += 10
            
            return score
            
        except Exception:
            return 0
    
    def _is_good_investment(self, analysis: Dict) -> bool:
        """Determine if property is a good investment"""
        try:
            # Property needs a minimum score of 70
            return (
                analysis.get('investment_score', 0) >= 70 and
                analysis.get('price_per_sqft', float('inf')) < self.price_per_sqft_threshold and
                analysis.get('estimated_roi', 0) >= self.roi_threshold
            )
        except Exception:
            return False
