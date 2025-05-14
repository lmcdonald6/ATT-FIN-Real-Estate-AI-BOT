#!/usr/bin/env python3
"""
Neighborhood Full Analysis Pipeline

This script integrates all components of the autonomous sentiment analysis infrastructure
to provide a complete neighborhood analysis workflow.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our components
from src.advanced.agent_router import ManusAgentRouter, choose_agent_source
from src.advanced.refresh_agent import SentimentRefreshAgent
from src.advanced.reputation_index import NeighborhoodReputationIndex


async def run_neighborhood_analysis(zip_code: str) -> Dict[str, Any]:
    """
    Executes the full neighborhood analysis loop:
    1. Determines data source via Manus router
    2. Refreshes sentiment data if stale or missing
    3. Computes final neighborhood reputation index
    
    Args:
        zip_code: The ZIP code to analyze
        
    Returns:
        Dictionary with analysis results
    """
    print(f"\n🧭 Routing request → ZIP: {zip_code}")
    router = ManusAgentRouter()
    source = router.choose_agent_source(zip_code)
    print(f"📡 Routed to source: {source}")
    
    print(f"🔄 Checking freshness + refreshing if needed...")
    refresh_agent = SentimentRefreshAgent()
    refresh_result = await refresh_agent.refresh_sentiment_for_zip(zip_code)
    
    if refresh_result.get('refreshed', False):
        print(f"✅ Data refreshed successfully")
        if 'summary' in refresh_result:
            print(f"📝 Summary: {refresh_result['summary'][:100]}...")
    else:
        print(f"ℹ️ Using existing data: {refresh_result.get('reason', 'unknown reason')}")
    
    print(f"📊 Computing reputation score...")
    reputation_index = NeighborhoodReputationIndex()
    index_result = reputation_index.compute_reputation_index(zip_code)
    
    # Report the source result back to the router
    success = index_result.get('confidence_score', 0) > 0.3  # Consider it successful if we got a decent confidence score
    router.report_source_result(zip_code, source, success)
    
    return {
        "zip": zip_code,
        "source": source,
        "score_report": index_result
    }


async def analyze_multiple_neighborhoods(zip_codes: List[str]) -> List[Dict[str, Any]]:
    """
    Analyze multiple neighborhoods in parallel.
    
    Args:
        zip_codes: List of ZIP codes to analyze
        
    Returns:
        List of analysis results
    """
    results = []
    for zip_code in zip_codes:
        result = await run_neighborhood_analysis(zip_code)
        results.append(result)
        
        print("\n🏘️ Neighborhood Reputation Summary:")
        print(json.dumps(result, indent=2))
    
    return results


async def main():
    """
    Main entry point for the neighborhood analysis pipeline.
    """
    # Example ZIP codes to analyze
    zips = ["30318", "11238", "90210"]
    
    print("🚀 Starting Neighborhood Analysis Pipeline")
    print(f"📍 Analyzing {len(zips)} neighborhoods: {', '.join(zips)}")
    
    results = await analyze_multiple_neighborhoods(zips)
    
    print("\n✅ Analysis complete!")
    print(f"📊 Average reputation score: {sum(r['score_report'].get('overall_score', 0) for r in results) / len(results):.2f}")


if __name__ == "__main__":
    asyncio.run(main())
