"""API endpoints for market analysis and opportunity detection."""
from fastapi import FastAPI, HTTPException, Query
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path

from ..analysis.market_predictor import MarketPredictor
from ..analysis.neighborhood_scorer import NeighborhoodScorer
from ..analysis.investment_ranker import InvestmentRanker
from ..analysis.opportunity_detector import OpportunityDetector
from ..visualization.market_visualizer import MarketVisualizer
from ..integrations.data_sources import DataSourceIntegrator

app = FastAPI(title="Real Estate Market Analysis API")

# Initialize components
data_integrator = DataSourceIntegrator()
market_predictor = MarketPredictor()
neighborhood_scorer = NeighborhoodScorer()
investment_ranker = InvestmentRanker()
opportunity_detector = OpportunityDetector()
market_visualizer = MarketVisualizer()

@app.post("/api/analyze-market")
async def analyze_market(
    redfin_file: str,
    attom_file: str,
    market_file: str,
    zip_code: Optional[str] = None
) -> Dict:
    """Analyze market conditions and opportunities."""
    try:
        # Load and integrate data
        redfin_data = data_integrator.load_redfin_data(redfin_file)
        attom_data = data_integrator.load_attom_data(attom_file)
        market_data = data_integrator.load_market_data(market_file)
        
        # Filter by zip code if provided
        if zip_code:
            redfin_data = redfin_data[redfin_data['zip_code'] == zip_code]
            attom_data = attom_data[attom_data['zip_code'] == zip_code]
            market_data = market_data[market_data['zip_code'] == zip_code]
        
        # Merge data sources
        property_data = data_integrator.merge_data_sources(redfin_data, attom_data)
        
        # Generate analysis
        market_prediction = market_predictor.predict_trends(market_data)
        neighborhood_scores = neighborhood_scorer.score_neighborhoods(property_data)
        investment_rankings = investment_ranker.rank_opportunities(property_data)
        opportunities = opportunity_detector.find_opportunities(
            market_data,
            property_data
        )
        
        # Create visualizations
        dashboard = market_visualizer.create_opportunity_dashboard(
            opportunities,
            market_data
        )
        
        # Export visualizations
        output_dir = Path("output/dashboards")
        output_dir.mkdir(parents=True, exist_ok=True)
        market_visualizer.export_dashboard(dashboard, str(output_dir))
        
        return {
            "market_prediction": market_prediction,
            "neighborhood_scores": neighborhood_scores,
            "investment_rankings": investment_rankings,
            "opportunities": opportunities,
            "dashboard_url": str(output_dir)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/market-health")
async def get_market_health(
    market_file: str,
    zip_code: Optional[str] = None
) -> Dict:
    """Get market health indicators."""
    try:
        # Load market data
        market_data = data_integrator.load_market_data(market_file)
        
        # Filter by zip code if provided
        if zip_code:
            market_data = market_data[market_data['zip_code'] == zip_code]
        
        # Calculate market health metrics
        health_metrics = {
            "price_trends": market_predictor.analyze_price_trends(market_data),
            "inventory_levels": market_predictor.analyze_inventory(market_data),
            "market_efficiency": market_predictor.analyze_market_efficiency(market_data),
            "sales_velocity": market_predictor.analyze_sales_velocity(market_data)
        }
        
        # Create health dashboard
        dashboard = market_visualizer.create_market_health_dashboard(market_data)
        
        # Export visualizations
        output_dir = Path("output/health_dashboard")
        output_dir.mkdir(parents=True, exist_ok=True)
        market_visualizer.export_dashboard(dashboard, str(output_dir))
        
        return {
            "health_metrics": health_metrics,
            "dashboard_url": str(output_dir)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/opportunities")
async def get_opportunities(
    redfin_file: str,
    attom_file: str,
    market_file: str,
    min_confidence: float = Query(0.7, ge=0, le=1),
    zip_code: Optional[str] = None
) -> List[Dict]:
    """Get investment opportunities."""
    try:
        # Load and integrate data
        redfin_data = data_integrator.load_redfin_data(redfin_file)
        attom_data = data_integrator.load_attom_data(attom_file)
        market_data = data_integrator.load_market_data(market_file)
        
        # Filter by zip code if provided
        if zip_code:
            redfin_data = redfin_data[redfin_data['zip_code'] == zip_code]
            attom_data = attom_data[attom_data['zip_code'] == zip_code]
            market_data = market_data[market_data['zip_code'] == zip_code]
        
        # Merge data sources
        property_data = data_integrator.merge_data_sources(redfin_data, attom_data)
        
        # Find opportunities
        opportunities = opportunity_detector.find_opportunities(
            market_data,
            property_data,
            min_confidence=min_confidence
        )
        
        return opportunities
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/neighborhood-scores")
async def get_neighborhood_scores(
    redfin_file: str,
    attom_file: str,
    zip_code: Optional[str] = None
) -> Dict:
    """Get neighborhood scores."""
    try:
        # Load and integrate data
        redfin_data = data_integrator.load_redfin_data(redfin_file)
        attom_data = data_integrator.load_attom_data(attom_file)
        
        # Filter by zip code if provided
        if zip_code:
            redfin_data = redfin_data[redfin_data['zip_code'] == zip_code]
            attom_data = attom_data[attom_data['zip_code'] == zip_code]
        
        # Merge data sources
        property_data = data_integrator.merge_data_sources(redfin_data, attom_data)
        
        # Calculate neighborhood scores
        scores = neighborhood_scorer.score_neighborhoods(property_data)
        
        return scores
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export-analysis")
async def export_analysis(
    analysis_data: Dict,
    output_file: str
) -> Dict:
    """Export analysis results to Excel."""
    try:
        # Convert analysis data to DataFrame
        df = pd.DataFrame(analysis_data.get('opportunities', []))
        
        # Export to Excel
        data_integrator.export_to_excel(df, output_file)
        
        return {"message": f"Analysis exported to {output_file}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/data-validation")
async def validate_data_sources(
    redfin_file: str,
    attom_file: str,
    market_file: str
) -> Dict:
    """Validate data sources for quality and completeness."""
    try:
        # Load data
        redfin_data = data_integrator.load_redfin_data(redfin_file)
        attom_data = data_integrator.load_attom_data(attom_file)
        market_data = data_integrator.load_market_data(market_file)
        
        # Validate each source
        validation_results = {
            "redfin": data_integrator.validate_data(redfin_data, "redfin"),
            "attom": data_integrator.validate_data(attom_data, "attom"),
            "market": data_integrator.validate_data(market_data, "market")
        }
        
        return validation_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
