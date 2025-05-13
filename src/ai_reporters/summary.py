"""AI-powered summary generation."""

from typing import Dict
import json

def generate_summary(
    property_data: Dict,
    scores: Dict,
    recommendation: str
) -> str:
    """Generate a markdown summary of the analysis."""
    
    # Format risk factors
    risk_list = "\n".join([f"- {risk}" for risk in scores.get("risk_factors", [])])
    if not risk_list:
        risk_list = "- No significant risks identified"
    
    # Create summary
    summary = f"""
# Property Analysis Summary

## 🎯 Investment Metrics
- **Overall Score:** {scores.get('investment_score', 0)}/100
- **Risk Score:** {scores.get('risk_score', 0)}/100
- **Recommendation:** {recommendation}

## 📊 Market Indicators
- **Market Growth:** {property_data['market_stats']['price_growth_1y']}% (1Y)
- **Median Price:** ${property_data['market_stats']['median_home_price']:,}
- **Cap Rate:** {property_data['market_stats']['cap_rate_avg']}%

## ⚠️ Risk Assessment
{risk_list}

## 👥 Demographics
- **Population Growth:** {property_data['signals']['demographics']['population_growth']}%
- **Median Income:** ${property_data['signals']['demographics']['median_income']:,}
- **Employment Rate:** {property_data['signals']['demographics']['employment_rate']*100:.1f}%

## 🏘️ Neighborhood
- **Crime Score:** {scores['component_scores']['crime']:.1f}/100
- **Transit Score:** {property_data['signals']['transit']['transit_score']}/100
- **Development Score:** {property_data['signals']['zoning']['development_potential']}/100

## 💡 Investment Opportunities
"""
    
    # Add opportunities
    for opp in property_data.get('opportunities', []):
        summary += f"- **{opp['type'].title()}:** {opp['description']} (ROI: {opp['roi_estimate']}%)\n"
    
    return summary

def store_results(
    property_data: Dict,
    scores: Dict,
    recommendation: str,
    use_airtable: bool = False
) -> None:
    """Store analysis results in Airtable or locally."""
    if use_airtable:
        # TODO: Implement Airtable storage
        pass
    else:
        # Store locally as JSON
        result = {
            "property_data": property_data,
            "scores": scores,
            "recommendation": recommendation,
            "summary": generate_summary(property_data, scores, recommendation)
        }
        
        with open("analysis_results.json", "w") as f:
            json.dump(result, f, indent=2)
