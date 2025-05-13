"""Custom rule-based analysis reporter."""

from typing import Dict, List
from .base import AIReporterBase

class CustomReporter(AIReporterBase):
    """Rule-based implementation of the AI reporter."""
    
    def __init__(self, temperature: float = 0.3):
        """Initialize the custom reporter."""
        super().__init__(temperature)
    
    async def generate_investment_summary(self, data: Dict) -> Dict[str, str]:
        """Generate an investment opportunity summary using rule-based analysis."""
        try:
            # Extract key metrics
            signals = data.get("signals", {})
            market_stats = data.get("market_stats", {})
            
            # Calculate overall investment potential
            scores = [
                signals.get("permits", {}).get("permit_score", 50),
                signals.get("demographics", {}).get("migration_score", 50),
                signals.get("crime", {}).get("crime_score", 50),
                signals.get("transit", {}).get("transit_score", 50),
                signals.get("zoning", {}).get("zoning_score", 50)
            ]
            overall_score = sum(scores) / len(scores)
            
            # Generate summary
            summary = self._generate_summary_text(overall_score, market_stats)
            pros = self._identify_advantages(signals, market_stats)
            cons = self._identify_risks(signals, market_stats)
            strategy = self._recommend_strategy(overall_score, signals, market_stats)
            
            return {
                "summary": summary,
                "pros": pros,
                "cons": cons,
                "strategy": strategy
            }
            
        except Exception as e:
            return {
                "summary": f"Error generating summary: {str(e)}",
                "pros": [],
                "cons": [],
                "strategy": "Error occurred"
            }
    
    async def generate_risk_report(self, data: Dict) -> Dict[str, str]:
        """Generate a detailed risk analysis report using rule-based analysis."""
        try:
            signals = data.get("signals", {})
            market_stats = data.get("market_stats", {})
            
            # Assess risk level
            risk_factors = self._calculate_risk_factors(signals, market_stats)
            risk_level = self._determine_risk_level(risk_factors)
            
            return {
                "risk_level": risk_level,
                "market_risks": self._identify_market_risks(signals, market_stats),
                "property_risks": self._identify_property_risks(signals, market_stats),
                "mitigation": self._suggest_risk_mitigation(risk_factors)
            }
            
        except Exception as e:
            return {
                "risk_level": "Error",
                "market_risks": [],
                "property_risks": [],
                "mitigation": f"Error generating risk report: {str(e)}"
            }
    
    async def generate_neighborhood_snapshot(self, data: Dict) -> Dict[str, str]:
        """Generate a neighborhood analysis snapshot using rule-based analysis."""
        try:
            signals = data.get("signals", {})
            market_stats = data.get("market_stats", {})
            
            return {
                "overview": self._generate_neighborhood_overview(signals),
                "demographics": self._analyze_demographics(signals.get("demographics", {})),
                "trends": self._identify_trends(signals, market_stats),
                "opportunities": self._identify_opportunities(signals, market_stats)
            }
            
        except Exception as e:
            return {
                "overview": f"Error generating snapshot: {str(e)}",
                "demographics": "Error",
                "trends": [],
                "opportunities": []
            }
    
    def _generate_summary_text(self, overall_score: float, market_stats: Dict) -> str:
        """Generate summary text based on overall score and market stats."""
        if overall_score >= 80:
            return f"Excellent investment opportunity with a score of {overall_score:.1f}/100. Market shows strong fundamentals with {market_stats.get('price_growth_1y', 0)}% annual price growth."
        elif overall_score >= 60:
            return f"Good investment potential with a score of {overall_score:.1f}/100. Market demonstrates stable conditions."
        else:
            return f"Moderate investment opportunity with a score of {overall_score:.1f}/100. Consider careful due diligence."
    
    def _identify_advantages(self, signals: Dict, market_stats: Dict) -> List[str]:
        """Identify key advantages based on signals and market stats."""
        pros = []
        
        # Check permits
        if signals.get("permits", {}).get("permit_score", 0) > 70:
            pros.append("Strong development activity indicating growth")
        
        # Check demographics
        demo = signals.get("demographics", {})
        if demo.get("population_growth", 0) > 2:
            pros.append(f"High population growth at {demo.get('population_growth')}%")
        
        # Check market stats
        if market_stats.get("price_growth_1y", 0) > 5:
            pros.append(f"Strong price appreciation at {market_stats.get('price_growth_1y')}%")
        
        return pros if pros else ["No significant advantages identified"]
    
    def _identify_risks(self, signals: Dict, market_stats: Dict) -> List[str]:
        """Identify key risks based on signals and market stats."""
        risks = []
        
        # Check crime
        if signals.get("crime", {}).get("crime_score", 100) < 50:
            risks.append("Higher than average crime rates")
        
        # Check market stats
        if market_stats.get("rental_vacancy", 0) > 7:
            risks.append(f"High rental vacancy rate at {market_stats.get('rental_vacancy')}%")
        
        return risks if risks else ["No significant risks identified"]
    
    def _recommend_strategy(self, overall_score: float, signals: Dict, market_stats: Dict) -> str:
        """Recommend investment strategy based on analysis."""
        if overall_score >= 80:
            return "Aggressive investment recommended. Consider both residential and commercial opportunities."
        elif overall_score >= 60:
            return "Moderate investment approach. Focus on residential properties with value-add potential."
        else:
            return "Conservative approach recommended. Look for deep value opportunities and strong cash flow."
