# Development Guide

## Getting Started

### Prerequisites
1. Python 3.8+
2. Redis
3. PostgreSQL
4. Node.js 14+
5. Docker and Docker Compose
6. Git

### Development Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/wholesale.git
cd wholesale
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start development services:
```bash
docker-compose -f docker-compose.dev.yml up -d
```

## Project Structure

```
wholesale/
├── src/
│   ├── api_gateway/      # API Gateway service
│   ├── analysis/         # Analysis services
│   │   ├── hyperlocal/   # Hyperlocal analysis
│   │   └── predictive/   # Predictive analysis
│   ├── cache/           # Caching service
│   ├── interface/       # User interfaces
│   │   ├── voice/       # Voice interface
│   │   └── web/         # Web interface
│   └── utils/           # Shared utilities
├── tests/
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── e2e/           # End-to-end tests
├── docs/              # Documentation
├── scripts/           # Development scripts
└── docker/           # Docker configurations
```

## Development Workflow

### 1. Code Style
- Follow PEP 8 guidelines
- Use type hints
- Document functions and classes
- Keep functions focused and small

Example:
```python
from typing import Dict, Optional

def analyze_property(
    address: str,
    zipcode: str,
    *,
    include_history: bool = False
) -> Dict:
    """Analyze a property using address and ZIP code.

    Args:
        address: Property street address
        zipcode: Property ZIP code
        include_history: Include historical data

    Returns:
        Dict containing property analysis
    """
    ...
```

### 2. Testing

#### Unit Tests
```bash
# Run all unit tests
pytest tests/unit

# Run with coverage
pytest --cov=src tests/unit

# Run specific test file
pytest tests/unit/test_market_cache.py
```

#### Integration Tests
```bash
# Run integration tests
pytest tests/integration

# Run with specific mark
pytest -m "slow" tests/integration
```

#### E2E Tests
```bash
# Run end-to-end tests
pytest tests/e2e
```

### 3. Git Workflow

1. Create feature branch:
```bash
git checkout -b feature/new-feature
```

2. Make changes and commit:
```bash
git add .
git commit -m "feat: add new feature"
```

3. Push changes:
```bash
git push origin feature/new-feature
```

4. Create pull request

### 4. Documentation

- Update API documentation for new endpoints
- Add docstrings to new functions/classes
- Update architecture docs for major changes
- Include examples in README

### 5. Performance

#### Profiling
```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    # Your code here
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()
```

#### Benchmarking
```python
import timeit

def benchmark_function():
    setup = "from your_module import your_function"
    stmt = "your_function()"
    result = timeit.timeit(stmt, setup, number=1000)
    print(f"Average time: {result/1000:.6f} seconds")
```

### 6. Debugging

#### Using pdb
```python
import pdb

def debug_function():
    x = calculate_something()
    pdb.set_trace()  # Debugger will stop here
    y = process_result(x)
```

#### Using logging
```python
import logging

logger = logging.getLogger(__name__)

def process_data():
    logger.debug("Processing data...")
    try:
        result = complex_operation()
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
```

## Common Tasks

### 1. Adding a New Service

1. Create service directory:
```bash
mkdir src/new_service
touch src/new_service/__init__.py
```

2. Implement service class:
```python
from typing import Dict

class NewService:
    def __init__(self, config: Dict):
        self.config = config
        
    async def initialize(self):
        # Setup code
        pass
        
    async def process(self, data: Dict):
        # Processing logic
        pass
```

3. Add tests:
```python
import pytest
from src.new_service import NewService

def test_new_service():
    service = NewService({})
    result = await service.process({})
    assert result is not None
```

### 2. Database Migrations

```bash
# Create migration
alembic revision -m "add new table"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### 3. Adding Dependencies

1. Add to requirements.txt:
```
new-package==1.2.3
```

2. Update dependencies:
```bash
pip install -r requirements.txt
```

3. Update tests and documentation

## Troubleshooting

### Common Issues

1. Redis Connection:
```python
import redis
from redis.exceptions import ConnectionError

try:
    redis_client = redis.Redis()
    redis_client.ping()
except ConnectionError:
    print("Redis not running")
```

2. Database Connection:
```python
import psycopg2

try:
    conn = psycopg2.connect(
        dbname="wholesale",
        user="user",
        password="pass",
        host="localhost"
    )
except psycopg2.Error as e:
    print(f"Database error: {e}")
```

3. API Gateway Issues:
```bash
# Check logs
docker logs api-gateway

# Check endpoints
curl -v http://localhost:8000/health
```

## Deployment

### Local Deployment
```bash
docker-compose up --build -d
```

### Staging Deployment
```bash
./scripts/deploy.sh staging
```

### Production Deployment
```bash
./scripts/deploy.sh production
```

## Resources

- [Python Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Redis Documentation](https://redis.io/documentation)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
