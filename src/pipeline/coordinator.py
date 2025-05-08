"""Market analysis pipeline coordinator."""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..cache.market_cache import MarketCache
from ..integrations.data_validators import MarketDataValidator
from ..analysis.market_predictor import MarketPredictor
from ..analysis.neighborhood_scorer import NeighborhoodScorer
from ..analysis.opportunity_detector import OpportunityDetector
from ..analysis.cma_analyzer import CMAAnalyzer
from ..utils.error_handler import (
    handle_errors,
    DataValidationError,
    DataSourceError,
    error_logger
)

logger = logging.getLogger(__name__)

class PipelineCoordinator:
    """Coordinates the market analysis pipeline."""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.cache = MarketCache(config.get('redis_config'))
        self.validator = MarketDataValidator(config.get('validation_config'))
        self.market_predictor = MarketPredictor(config.get('predictor_config'))
        self.neighborhood_scorer = NeighborhoodScorer(config.get('scorer_config'))
        self.opportunity_detector = OpportunityDetector(config.get('detector_config'))
        self.cma_analyzer = CMAAnalyzer(config.get('cma_config'))
    
    @handle_errors({
        DataValidationError: 'VALIDATION_ERROR',
        DataSourceError: 'DATA_SOURCE_ERROR'
    })
    async def analyze_market(self,
                           zip_code: str,
                           analysis_type: str,
                           params: Dict[str, Any]) -> Dict[str, Any]:
        """Run market analysis pipeline."""
        # Check cache first
        cached_result = self.cache.get_market_analysis(
            zip_code,
            analysis_type,
            params
        )
        if cached_result:
            logger.info(f"Cache hit for {zip_code} {analysis_type}")
            return cached_result
        
        # Get market data
        market_data = await self._get_market_data(zip_code)
        
        # Validate data
        validation_errors = self.validator.validate_market_trends(market_data)
        if validation_errors:
            error_logger.log_validation_error(validation_errors, 'market_data')
            if any(e['error'] == 'critical' for e in validation_errors):
                raise DataValidationError(
                    "Critical validation errors in market data",
                    'VALIDATION_ERROR',
                    {'errors': validation_errors}
                )
        
        # Run analysis based on type
        result = await self._run_analysis(
            analysis_type,
            market_data,
            params
        )
        
        # Cache results
        self.cache.cache_market_analysis(
            zip_code,
            analysis_type,
            params,
            result
        )
        
        return result
    
    async def _get_market_data(self, zip_code: str) -> Dict[str, Any]:
        """Get market data from various sources."""
        try:
            # Get data from different sources
            redfin_data = await self._fetch_redfin_data(zip_code)
            attom_data = await self._fetch_attom_data(zip_code)
            
            # Merge data
            market_data = self._merge_market_data(
                redfin_data,
                attom_data
            )
            
            return market_data
            
        except Exception as e:
            error_logger.log_error(
                e,
                {'zip_code': zip_code}
            )
            raise DataSourceError(
                f"Failed to fetch market data: {str(e)}",
                'DATA_SOURCE_ERROR'
            )
    
    async def _run_analysis(self,
                          analysis_type: str,
                          market_data: Dict[str, Any],
                          params: Dict[str, Any]) -> Dict[str, Any]:
        """Run specific type of analysis."""
        analysis_map = {
            'market_prediction': self._run_market_prediction,
            'neighborhood_score': self._run_neighborhood_scoring,
            'opportunity_detection': self._run_opportunity_detection,
            'cma': self._run_cma_analysis
        }
        
        if analysis_type not in analysis_map:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
            
        return await analysis_map[analysis_type](market_data, params)
    
    async def _run_market_prediction(self,
                                   market_data: Dict[str, Any],
                                   params: Dict[str, Any]) -> Dict[str, Any]:
        """Run market prediction analysis."""
        return await self.market_predictor.predict_trends(
            market_data,
            params.get('timeframe', '12M')
        )
    
    async def _run_neighborhood_scoring(self,
                                     market_data: Dict[str, Any],
                                     params: Dict[str, Any]) -> Dict[str, Any]:
        """Run neighborhood scoring analysis."""
        return await self.neighborhood_scorer.calculate_score(
            market_data,
            params.get('metrics', ['price', 'schools', 'crime'])
        )
    
    async def _run_opportunity_detection(self,
                                      market_data: Dict[str, Any],
                                      params: Dict[str, Any]) -> Dict[str, Any]:
        """Run opportunity detection analysis."""
        return await self.opportunity_detector.find_opportunities(
            market_data,
            params.get('criteria', {})
        )
    
    async def _run_cma_analysis(self,
                              market_data: Dict[str, Any],
                              params: Dict[str, Any]) -> Dict[str, Any]:
        """Run CMA analysis."""
        return await self.cma_analyzer.analyze_comparables(
            market_data,
            params.get('property_details', {})
        )
    
    def _merge_market_data(self,
                          redfin_data: Dict[str, Any],
                          attom_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge market data from different sources."""
        # Implement sophisticated merging logic here
        merged_data = {
            'timestamp': datetime.now().isoformat(),
            'sources': ['redfin', 'attom'],
            'metrics': {}
        }
        
        # Merge price data
        merged_data['metrics']['price'] = self._merge_price_data(
            redfin_data.get('price_data', {}),
            attom_data.get('price_data', {})
        )
        
        # Merge inventory data
        merged_data['metrics']['inventory'] = self._merge_inventory_data(
            redfin_data.get('inventory_data', {}),
            attom_data.get('inventory_data', {})
        )
        
        # Merge market trends
        merged_data['metrics']['trends'] = self._merge_trend_data(
            redfin_data.get('trend_data', {}),
            attom_data.get('trend_data', {})
        )
        
        return merged_data
    
    def _merge_price_data(self,
                         redfin_prices: Dict[str, Any],
                         attom_prices: Dict[str, Any]) -> Dict[str, Any]:
        """Merge price data with weighting."""
        # Implement sophisticated price merging logic
        return {
            'median_price': (
                redfin_prices.get('median', 0) * 0.6 +
                attom_prices.get('median', 0) * 0.4
            ),
            'average_price': (
                redfin_prices.get('average', 0) * 0.6 +
                attom_prices.get('average', 0) * 0.4
            ),
            'price_range': {
                'min': min(
                    redfin_prices.get('min', float('inf')),
                    attom_prices.get('min', float('inf'))
                ),
                'max': max(
                    redfin_prices.get('max', 0),
                    attom_prices.get('max', 0)
                )
            }
        }
    
    def _merge_inventory_data(self,
                            redfin_inventory: Dict[str, Any],
                            attom_inventory: Dict[str, Any]) -> Dict[str, Any]:
        """Merge inventory data with validation."""
        return {
            'active_listings': max(
                redfin_inventory.get('active', 0),
                attom_inventory.get('active', 0)
            ),
            'pending_listings': max(
                redfin_inventory.get('pending', 0),
                attom_inventory.get('pending', 0)
            ),
            'days_on_market': (
                redfin_inventory.get('dom', 0) * 0.7 +
                attom_inventory.get('dom', 0) * 0.3
            )
        }
    
    def _merge_trend_data(self,
                         redfin_trends: Dict[str, Any],
                         attom_trends: Dict[str, Any]) -> Dict[str, Any]:
        """Merge market trend data with validation."""
        return {
            'price_trend': self._calculate_weighted_trend(
                redfin_trends.get('price_trend', []),
                attom_trends.get('price_trend', [])
            ),
            'inventory_trend': self._calculate_weighted_trend(
                redfin_trends.get('inventory_trend', []),
                attom_trends.get('inventory_trend', [])
            ),
            'dom_trend': self._calculate_weighted_trend(
                redfin_trends.get('dom_trend', []),
                attom_trends.get('dom_trend', [])
            )
        }
    
    def _calculate_weighted_trend(self,
                                redfin_trend: List[float],
                                attom_trend: List[float],
                                redfin_weight: float = 0.6) -> List[float]:
        """Calculate weighted trend from multiple sources."""
        if not redfin_trend and not attom_trend:
            return []
            
        if not redfin_trend:
            return attom_trend
            
        if not attom_trend:
            return redfin_trend
            
        # Use the shorter length for alignment
        length = min(len(redfin_trend), len(attom_trend))
        attom_weight = 1 - redfin_weight
        
        return [
            redfin_trend[i] * redfin_weight + attom_trend[i] * attom_weight
            for i in range(length)
        ]
