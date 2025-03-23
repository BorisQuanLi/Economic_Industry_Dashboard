"""
Production configuration for the application.
"""

import os

class Config:
    """Production configuration."""
    
    DEBUG = False
    TESTING = False
    
    # Database settings
    DB_CONFIG = {
        'host': os.environ.get('DB_HOST'),
        'port': int(os.environ.get('DB_PORT', 5432)),
        'database': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASSWORD'),
    }
    
    # API settings
    API_CONFIG = {
        'debug': False,
        'host': '0.0.0.0',
        'port': int(os.environ.get('PORT', 5000)),
    }
    
    # Logging settings
    LOG_CONFIG = {
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    }
    
    # Cache settings
    CACHE_CONFIG = {
        'enabled': True,
        'timeout': int(os.environ.get('CACHE_TIMEOUT', 600)),  # 10 minutes
    }

    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production environment")
