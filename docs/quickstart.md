# Quick Start Guide

> "From setup to first insight in 5 minutes."

## 🚀 Zero to Analysis in 3 Steps

### 1. Get Your API Key
```bash
# Sign up and get your key instantly
curl -X POST https://api.realestate.ai/signup \
  -d '{"email": "your@email.com"}' \
  -H "Content-Type: application/json"
```

### 2. Install & Configure
```bash
# One command to get everything running
docker-compose up -d

# Configure your API key
echo "REAL_ESTATE_AI_KEY=your_key_here" > .env
```

### 3. Run Your First Analysis
```python
from wholesale import RealEstateAI

ai = RealEstateAI()
insights = await ai.analyze_neighborhood("90210")
print(f"Growth Potential: {insights.growth_potential}%")
```

## 🎯 What You Get Immediately

- **Live Market Dashboard**: See real-time changes in your target areas
- **Opportunity Alerts**: Get notified when our AI spots potential deals
- **Neighborhood Insights**: Access block-by-block analysis of any area

## 📊 Sample Results

Here's what users typically see in their first week:

| Metric | Impact |
|--------|---------|
| Time Saved | 4.2x faster research |
| New Opportunities | +127% more leads |
| Prediction Accuracy | 93% success rate |

## 🛠 Next Steps

1. [Connect Your Data Sources](integrations.md)
2. [Set Up Custom Alerts](alerts.md)
3. [Configure Your AI Models](ml_config.md)

Need help? [Join our Discord](https://discord.gg/realestate-ai) - we're usually online.
