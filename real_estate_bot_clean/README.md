# Real Estate AI Wholesaling System

A comprehensive AI-powered system for real estate wholesaling, built with a hybrid data approach combining mock data generation and selective ATTOM API enrichment.

## Current MVP Features

### 1. Market Analysis Engine
- Advanced market analysis toolkit with machine learning integration
- Seasonal price adjustment modeling
- Property value predictions with confidence scoring
- Market phase detection and momentum tracking
- Hybrid data approach:
  - Mock data generation for rapid development
  - Selective ATTOM API enrichment (400 reports/month)
  - 24-hour response caching

### 2. Data Management
- Efficient data storage and caching system
- Smart API usage tracking
- Location-aware property generation
- Market-specific price adjustments

## Roadmap

### Phase 1: Deal Finding (In Progress)
- [x] Basic market analysis
- [x] Property value predictions
- [x] Seasonal adjustments
- [ ] Distressed property indicators
  - Tax liens integration
  - Foreclosure data
  - Vacancy analysis
- [ ] Automated lead scoring
- [ ] Direct mail campaign optimization

### Phase 2: Deal Analysis (Next)
- [ ] Enhanced ARV calculations
- [ ] Repair cost estimation
- [ ] Profit potential scoring
- [ ] Comp analysis automation
- [ ] Risk assessment modeling
- [ ] Deal viability predictions

### Phase 3: Marketing Automation
- [ ] Lead management system
- [ ] Automated follow-up sequences
- [ ] Multi-channel outreach
  - SMS integration
  - Email automation
  - Social media targeting
- [ ] AI chatbot for lead qualification

### Phase 4: Buyer Network
- [ ] Cash buyer database
- [ ] Investor activity tracking
- [ ] Buyer preference modeling
- [ ] Deal matching algorithm
- [ ] Automated buyer outreach

### Phase 5: Market Intelligence
- [ ] Advanced price trend prediction
- [ ] Market hotspot identification
- [ ] Investment opportunity scoring
- [ ] Neighborhood analysis
- [ ] Economic indicator tracking

### Phase 6: Transaction Automation
- [ ] Smart contract generation
- [ ] Legal requirement checking
- [ ] Title company integration
- [ ] Document automation
- [ ] Closing process optimization

## AI Framework Implementation

### Phase 1: Hybrid Data Foundation (Completed)
- ✅ Mock data generation system
- ✅ ATTOM API integration (400 reports/month)
- ✅ Confidence scoring system
- ✅ Data freshness tracking
- ✅ 24-hour response caching
- ✅ Rate limiting and usage optimization

### Phase 2: Enhanced Data Integration (In Progress)
- 🔄 Tax assessor database integration
- 🔄 Public records API integration
- 🔄 Foreclosure data services
- 🔄 Title company data access
- 🔄 Cross-source data validation
- 🔄 Enhanced confidence scoring

### Phase 3: Advanced ML Pipeline (Planned)
- Natural Language Processing
  - Document analysis
  - Contract understanding
  - Market report generation
- Computer Vision
  - Property image analysis
  - Condition assessment
  - Renovation cost estimation
- Time Series Analysis
  - Market trend prediction
  - Seasonal adjustments
  - Price movement forecasting
- Recommendation Engine
  - Buyer-property matching
  - Investment opportunity scoring
  - Deal viability prediction

### Phase 4: AI Automation (Future)
- Workflow Automation
  - Smart task scheduling
  - Process optimization
  - Resource allocation
- Document Processing
  - Automated contract generation
  - Legal requirement validation
  - Title search automation
- Communication Systems
  - AI-powered chat interfaces
  - Automated follow-ups
  - Multi-channel outreach

### Phase 5: Advanced Analytics (Future)
- Market Intelligence
  - Deep market analysis
  - Investment hotspot detection
  - Risk assessment modeling
- Portfolio Optimization
  - Deal scoring algorithms
  - Portfolio balancing
  - Risk-reward optimization
- Predictive Analytics
  - Market movement prediction
  - Property value forecasting
  - Investment timing optimization

## Technical Architecture

### Current Implementation
1. Data Sources
   - Mock data generation for development speed
   - ATTOM API for selective data enrichment
   - Cached responses (24h expiration)

2. Analysis Engine
   - Machine learning models for price prediction
   - Market phase detection
   - Seasonal adjustment calculations
   - Confidence scoring system

3. API Management
   - Usage tracking and optimization
   - Rate limiting
   - Error handling
   - Response caching

### Planned Enhancements
1. Data Integration
   - Public records APIs
   - MLS data access
   - Tax assessor databases
   - Social media APIs
   - Title company systems

2. AI/ML Pipeline
   - Natural Language Processing for document analysis
   - Computer Vision for property image analysis
   - Time series forecasting for market predictions
   - Recommendation systems for buyer-property matching

3. Automation Systems
   - Task scheduling
   - Workflow automation
   - Document processing
   - Communication management

## Getting Started

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- ATTOM API key (for production)
- Git

### Installation

#### Windows
1. Clone the repository:
   ```powershell
   git clone https://github.com/yourusername/real_estate_bot.git
   cd real_estate_bot
   ```

2. Create and activate virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```powershell
   # Using PowerShell
   $env:ATTOM_API_KEY="your_key_here"
   
   # Or create a .env file
   echo "ATTOM_API_KEY=your_key_here" > .env
   ```

#### macOS/Linux
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/real_estate_bot.git
   cd real_estate_bot
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   # Using terminal
   export ATTOM_API_KEY="your_key_here"
   
   # Or create a .env file
   echo "ATTOM_API_KEY=your_key_here" > .env
   ```

### Configuration
The system uses environment variables for configuration. You can either:
1. Set them in your shell session as shown above
2. Create a `.env` file in the project root
3. Use your IDE's environment variable configuration

Required variables:
```
ATTOM_API_KEY=your_key_here          # Required for production
MOCK_DATA_ENABLED=true               # Optional, default: true
CACHE_TTL=86400                      # Optional, default: 24 hours
LOG_LEVEL=INFO                       # Optional, default: INFO
```

### Development Setup

#### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_gateway_new.py

# Run with coverage
python -m pytest --cov=src tests/
```

#### Code Style
We use black for code formatting and flake8 for linting:
```bash
# Format code
black src/ tests/

# Run linter
flake8 src/ tests/
```

### Usage
1. Initialize the market toolkit:
   ```python
   from src.analysis.market_toolkit import MarketToolkit
   toolkit = MarketToolkit()
   ```

2. Analyze a market:
   ```python
   results = toolkit.analyze_market("37215", properties)
   ```

3. Get property predictions:
   ```python
   predictions = toolkit.predict_property_values(properties, market_data)
   ```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License
Proprietary - All rights reserved

## Acknowledgments
- ATTOM API for property data
- scikit-learn for machine learning models
- pandas for data manipulation
