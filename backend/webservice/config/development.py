"""
Development configuration for the application.
"""

import os

class Config:
    """Development configuration."""
    
    DEBUG = True
    TESTING = False
    
    # Database settings
    DB_CONFIG = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': int(os.environ.get('DB_PORT', 5432)),
        'database': os.environ.get('DB_NAME', 'economic_dashboard'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', 'postgres'),
    }
    
    # API settings
    API_CONFIG = {
        'debug': True,
        'host': '0.0.0.0',
        'port': 5000,
    }
    
    # Logging settings
    LOG_CONFIG = {
        'level': 'DEBUG',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    }
    
    # Cache settings
    CACHE_CONFIG = {
        'enabled': True,
        'timeout': 300,  # 5 minutes
    }
