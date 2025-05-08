"""Global configuration settings."""
import os
from typing import Dict, Any

# Redis Configuration
REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'localhost'),
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'default_ttl': 3600  # 1 hour
}

# API Configuration
API_CONFIG = {
    'host': os.getenv('API_HOST', '0.0.0.0'),
    'port': int(os.getenv('API_PORT', 8000)),
    'debug': bool(os.getenv('API_DEBUG', True)),
    'workers': int(os.getenv('API_WORKERS', 4))
}

# Data Source Configuration
DATA_SOURCES = {
    'redfin': {
        'api_key': os.getenv('REDFIN_API_KEY', ''),
        'base_url': os.getenv('REDFIN_BASE_URL', 'https://api.redfin.com/v1'),
        'timeout': 30
    },
    'attom': {
        'api_key': os.getenv('ATTOM_API_KEY', ''),
        'base_url': os.getenv('ATTOM_BASE_URL', 'https://api.attomdata.com/v1'),
        'timeout': 30
    }
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    'market_trends': {
        'min_data_points': 10,
        'outlier_threshold': 2.0,
        'trend_window': '30D'
    },
    'neighborhood_score': {
        'weights': {
            'price_trend': 0.3,
            'inventory': 0.2,
            'days_on_market': 0.2,
            'school_rating': 0.15,
            'crime_rate': 0.15
        }
    },
    'investment_metrics': {
        'cap_rate_threshold': 0.05,
        'cash_flow_threshold': 200,
        'roi_threshold': 0.08
    }
}

# Cache Configuration
CACHE_CONFIG = {
    'market_analysis_ttl': 3600,  # 1 hour
    'property_data_ttl': 86400,   # 24 hours
    'neighborhood_score_ttl': 604800,  # 7 days
    'market_trends_ttl': 43200    # 12 hours
}

# Logging Configuration
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler'
        },
        'file': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.FileHandler',
            'filename': 'app.log'
        }
    },
    'loggers': {
        '': {
            'handlers': ['default', 'file'],
            'level': 'INFO',
            'propagate': True
        }
    }
}
