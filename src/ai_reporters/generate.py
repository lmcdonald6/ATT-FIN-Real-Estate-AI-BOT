"""AI Reporter factory and generation functions."""

import os
from typing import Dict, Optional
from .openai_reporter import OpenAIReporter
from .claude_reporter import ClaudeReporter
from .custom_reporter import CustomReporter

async def generate_summary(
    data: Dict,
    provider: str = None,
    temperature: float = 0.3
) -> Dict:
    """
    Generate AI-powered analysis using the specified or best available provider.
    
    Args:
        data: Analysis data including signals and market stats
        provider: AI provider to use (openai/claude/custom)
        temperature: AI temperature setting (0-1)
        
    Returns:
        Dict containing generated reports:
        - investment_summary
        - risk_report
        - neighborhood_snapshot
    """
    # Get provider from environment if not specified
    if not provider:
        provider = os.getenv("DEFAULT_AI_PROVIDER", "custom")
    
    # Initialize appropriate reporter
    reporter = _get_reporter(provider, temperature)
    
    # Generate all reports
    investment_summary = await reporter.generate_investment_summary(data)
    risk_report = await reporter.generate_risk_report(data)
    neighborhood_snapshot = await reporter.generate_neighborhood_snapshot(data)
    
    return {
        "investment_summary": investment_summary,
        "risk_report": risk_report,
        "neighborhood_snapshot": neighborhood_snapshot,
        "provider": provider
    }

def _get_reporter(provider: str, temperature: float):
    """Get the appropriate reporter instance based on provider."""
    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        return OpenAIReporter(temperature)
    elif provider == "claude" and os.getenv("CLAUDE_API_KEY"):
        return ClaudeReporter(temperature)
    else:
        # Fallback to custom reporter if specified provider is not available
        if provider != "custom":
            print(f"Warning: {provider} API key not found, falling back to custom reporter")
        return CustomReporter(temperature)
