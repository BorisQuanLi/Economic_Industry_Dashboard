"""
Application settings

This module contains configuration settings for the application.
"""

import os
from typing import Dict, Any

# Database settings
DB_CONFIG: Dict[str, Any] = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'database': os.environ.get('DB_NAME', 'economic_dashboard'),
    'user': os.environ.get('DB_USER', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres'),
}

# API settings
API_CONFIG: Dict[str, Any] = {
    'debug': os.environ.get('API_DEBUG', 'False').lower() == 'true',
    'host': os.environ.get('API_HOST', '0.0.0.0'),
    'port': int(os.environ.get('API_PORT', 5000)),
}

# Logging settings
LOG_CONFIG: Dict[str, Any] = {
    'level': os.environ.get('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}

# Caching settings
CACHE_CONFIG: Dict[str, Any] = {
    'enabled': os.environ.get('CACHE_ENABLED', 'True').lower() == 'true',
    'timeout': int(os.environ.get('CACHE_TIMEOUT', 300)),
}

# Query limits
DEFAULT_QUERY_LIMIT = int(os.environ.get('DEFAULT_QUERY_LIMIT', 100))
