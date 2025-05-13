# Installation Guide for ATT-FIN Real Estate AI BOT

This guide will help you set up and run all components of the Real Estate AI Bot, following the microservice architecture principles.

## Prerequisites

- Python 3.9+ installed
- Git installed
- Internet connection for downloading dependencies
- API keys for external services (OpenAI, Zillow, etc.)

## Step 1: Clone the Repository

```bash
git clone [your-repo-url]
cd ATT-FIN-Real-Estate-AI-BOT
```

## Step 2: Set Up Environment Variables

Create a `.env` file in the project root with the following variables:

```
# Airtable Configuration
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_airtable_base_id
AIRTABLE_TABLE_ID=your_airtable_table_id

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
DEFAULT_LLM_MODEL=gpt-4
MAX_TOKENS=4096
TEMPERATURE=0.7

# Other API Keys (as needed)
# ZILLOW_API_KEY=your_zillow_api_key
# REALTOR_API_KEY=your_realtor_api_key
```

## Step 3: Install Core Dependencies

Create and activate a virtual environment, then install the core dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 4: Set Up Each Microservice

### 4.1 Dashboard Service

```bash
cd dashboard_service
pip install -r requirements.txt  # If service has its own requirements
cd ..
```

### 4.2 Financial Analysis Service

```bash
cd financial_analysis_service
pip install -r requirements.txt  # If service has its own requirements
cd ..
```

### 4.3 Data Scraping Service

```bash
cd data_scraping_service
pip install -r requirements.txt
cd ..
```

### 4.4 Model Audit Service

```bash
cd model_audit_service
pip install -r requirements.txt
cd ..
```

### 4.5 AI Tools Directory

```bash
cd ai_tools_directory
pip install -r requirements.txt
cd ..
```

## Step 5: Running the Services

### 5.1 Run the Core API Service

```bash
uvicorn src.main:app --reload --port 8000
```

### 5.2 Run the Dashboard Service

In a new terminal:

```bash
cd dashboard_service
streamlit run app.py
```

The dashboard will be available at http://localhost:8501

### 5.3 Run the Financial Analysis Service

In a new terminal:

```bash
cd financial_analysis_service
uvicorn api:app --reload --port 8001
```

### 5.4 Run the Data Scraping Service

In a new terminal:

```bash
cd data_scraping_service
python main.py --location "New York, NY" --sync
```

To schedule periodic scraping:

```bash
python main.py --location "New York, NY" --schedule daily --interval 1 --sync
```

### 5.5 Run the Model Audit Service

In a new terminal:

```bash
cd model_audit_service
python main.py audit-price --model path/to/model.pkl --test-data path/to/test_data.csv --target price
```

### 5.6 Use the AI Tools Directory

In a new terminal:

```bash
cd ai_tools_directory
python main.py list  # List all available tools
python main.py integrate zillow_api_integration  # Integrate a tool
```

## Step 6: Docker Deployment (Optional)

If you want to deploy the services using Docker:

1. Make sure Docker and Docker Compose are installed
2. Run the following command:

```bash
docker-compose up -d
```

This will start all services in separate containers.

## Troubleshooting

### API Key Issues

If you encounter errors related to API keys, make sure:
- All required API keys are set in the `.env` file
- The `.env` file is in the correct location (project root)
- API keys are valid and have the necessary permissions

### Dependency Issues

If you encounter dependency-related errors:

```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Port Conflicts

If a port is already in use, change the port number in the run command:

```bash
uvicorn src.main:app --reload --port 8080  # Change from 8000 to 8080
```

## Next Steps

After installation, you can:

1. Explore the dashboard at http://localhost:8501
2. Use the API endpoints at http://localhost:8000/docs
3. Run data scraping jobs to collect real estate data
4. Perform financial analysis on properties
5. Audit AI models for reliability and fairness
6. Integrate additional AI tools from the directory

For more detailed information, refer to the documentation in the `docs/` directory.
