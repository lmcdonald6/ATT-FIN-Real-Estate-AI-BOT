# Real Estate Intelligence Core (REIC)

## Overview

The Real Estate Intelligence Core (REIC) is a category-defining platform that combines emotional market understanding with quantitative precision to provide unparalleled real estate analysis. This system follows microservice principles with clear boundaries between components and a layered temporal inference architecture.

## Key Features

### 1. Layered Inference Architecture

REIC uses a comprehensive temporal analysis framework with three layers:

- **Past Layer**: Historical context, cycles, and anchor points
- **Present Layer**: Real-time alerts, live buzz, and current listings
- **Current Layer**: Forecasts, simulations, and projections

### 2. Intelligence API Layer

A REST API that exposes the following endpoints:

- `/conversation/query`: Routes to GPT Master Agent
- `/market/trends`: Historical and current trend data
- `/sentiment/scores`: Sentiment by region/street
- `/market/forecasts`: Predictive analytics
- `/discovery/opportunities`: Sentiment+price divergence
- `/export/pdf`: PDF generation for summaries

The API now features a modular router-based architecture:

- **Neighborhood Router** (`/api/sentiment`): Sentiment analysis for neighborhoods
- **Forecast Router** (`/api/forecast`): Market forecasts for ZIP codes
- **Discovery Router** (`/api/discover`): Investment opportunity identification

### 3. Enhanced User Interface

- Voice input with Whisper transcription
- Chat history tracking and retrieval
- Export options (PDF, CSV, Excel)
- User profiles and preferences

### 4. Street-Level Analysis

- Granular analysis of specific streets
- Multi-platform data source integration
- Comparative analysis across neighborhoods

## Architecture

The system follows microservice principles:

1. **Separate Data Stores**
   - Property data, market analytics, ML models, and configurations are separate
   - Data isolation between services

2. **Single Responsibility**
   - Services are focused and specialized
   - Clear boundaries between components
   
3. **Modular API Design**
   - Router-based architecture with specialized endpoints
   - Clear separation of concerns
   - Domain-driven design
   
4. **Robust Export Functionality**
   - PDF generation with ReportLab
   - Multiple export formats (PDF, CSV, JSON, text)
   - Fallback mechanisms for reliability
   - Well-defined interfaces

3. **Domain-Driven Design**
   - Core domain: Real estate analysis
   - Clear bounded contexts
   - Well-defined aggregates

## Getting Started

### Prerequisites

- Python 3.9+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ATT-FIN-Real-Estate-AI-BOT.git
cd ATT-FIN-Real-Estate-AI-BOT

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### Running the System

#### 1. Run the API Server

```bash
python -m src.api.run_api_server
```

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs

#### 2. Run the Chat Interface

```bash
python -m src.dashboard.run_ai_chat
```

The chat interface will be available at http://localhost:8501

#### 3. Run the Street Sentiment Map

```bash
python -m src.dashboard.run_street_dashboard
```

The street sentiment map will be available at http://localhost:8502

## Usage Examples

### API Examples

```python
import requests
import json

# Query the conversation endpoint
response = requests.post(
    "http://localhost:8000/conversation/query",
    json={
        "query": "What's the investment potential for ZIP code 90210 over the next 5 years?",
        "context": {}
    }
)

result = response.json()
print(json.dumps(result, indent=2))

# Get market trends
response = requests.get(
    "http://localhost:8000/market/trends",
    params={
        "zip_code": "90210",
        "years_back": 5
    }
)

result = response.json()
print(json.dumps(result, indent=2))
```

### Chat Interface Examples

The chat interface supports natural language queries like:

- "What's the current sentiment in ZIP code 90210?"
- "Compare the investment potential of ZIP codes 10001 and 60601 over the next 3 years."
- "What are the historical market trends for ZIP code 94105 over the past decade?"
- "How safe is Main Street in ZIP code 90210?"

## Implementation Roadmap

### Phase 1: Integrate Past/Present/Future Model ✅
- Build inference_layer.py with 3 temporal modules
- Update Master Agent to call specific layer logic based on query
- Integrate street trend history and price forecasts

### Phase 2: Launch v1 REST API ✅
- Wrap real_estate_ai_orchestrator() into FastAPI /conversation/query
- Add /export/pdf to allow front-end to download reports
- Add /sentiment/scores to trigger refresh or return cached score

### Phase 3: Map-Based Sentiment Intelligence 🔄
- Normalize all sentiment + price data with geo-coordinates
- Build street_layer_engine() for block-level queries
- Render interactive sentiment + market overlays via Mapbox/Folium

## Strategic Advantage

What makes REIC unbeatable is the combination of emotional market understanding (sentiment + GPT) with quantitative precision (market + forecasts). Competitors lack:

- Human tone understanding
- Real-time buzz awareness
- Street-level emotion + trend synthesis

## License

This project is proprietary and confidential.

## Contact

For questions or support, please contact your system administrator.
