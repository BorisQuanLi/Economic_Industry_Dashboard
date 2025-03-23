"""
Application Configuration Management.

This module provides centralized configuration for all application components.
It includes configurations for database connections, AWS services, and environment-specific settings.

Key components:
- DatabaseConfig: Database connection settings
- AWSConfig: AWS service credentials and settings
- Config: Main configuration class with environment-specific factory methods

Usage:
    from etl.config import get_config
    
    # Get application config
    config = get_config()
    
    # Access database configuration
    db_uri = config.db.uri
    
    # Access AWS configuration
    aws_key = config.aws.access_key

Environment variables can override default settings.
"""

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    uri: str
    username: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    
    @classmethod
    def from_uri(cls, uri: str) -> 'DatabaseConfig':
        """Create a database config from a URI"""
        # Extract components from URI if needed
        # Example: postgresql://username:password@host:port/database
        return cls(uri=uri)

@dataclass
class AWSConfig:
    """AWS services configuration"""
    access_key: str
    secret_key: str
    region: str = 'us-east-1'
    s3_bucket: str = 'sp500-financial-data'
    redshift_uri: Optional[str] = None

@dataclass
class Config:
    """Application configuration"""
    db: DatabaseConfig
    aws: Optional[AWSConfig] = None
    env: str = 'dev'
    debug: bool = False
    testing: bool = False
    
    @classmethod
    def load(cls, env: str = None) -> 'Config':
        """Load configuration based on environment"""
        env = env or os.getenv('APP_ENV', 'dev')
        
        if env == 'dev':
            return cls.development()
        elif env == 'test':
            return cls.testing()
        elif env == 'prod':
            return cls.production()
        else:
            return cls.development()
    
    @classmethod
    def development(cls) -> 'Config':
        """Development environment configuration"""
        return cls(
            db=DatabaseConfig(
                uri=os.getenv('DB_URI', 'postgresql://dev_user:dev_pass@localhost:5432/sp500_dev'),
                username=os.getenv('DB_USERNAME', 'dev_user'),
                password=os.getenv('DB_PASSWORD', 'dev_pass'),
                host=os.getenv('DB_HOST', 'localhost'),
                port=int(os.getenv('DB_PORT', '5432')),
                database=os.getenv('DB_NAME', 'sp500_dev')
            ),
            aws=AWSConfig(
                access_key=os.getenv('AWS_ACCESS_KEY', 'dev_key'),
                secret_key=os.getenv('AWS_SECRET_KEY', 'dev_secret'),
                s3_bucket=os.getenv('S3_BUCKET', 'sp500-financial-data-dev'),
                redshift_uri=os.getenv('REDSHIFT_URI', '')
            ),
            env='dev',
            debug=True
        )
    
    @classmethod
    def testing(cls) -> 'Config':
        """Testing environment configuration"""
        return cls(
            db=DatabaseConfig(
                uri=os.getenv('TEST_DB_URI', 'postgresql://test_user:test_pass@localhost:5432/test_db'),
                username='test_user',
                password='test_pass',
                host='localhost',
                port=5432,
                database='test_db'
            ),
            env='test',
            testing=True
        )
    
    @classmethod
    def production(cls) -> 'Config':
        """Production environment configuration"""
        return cls(
            db=DatabaseConfig(
                uri=os.getenv('DB_URI', ''),
                username=os.getenv('DB_USERNAME', ''),
                password=os.getenv('DB_PASSWORD', ''),
                host=os.getenv('DB_HOST', ''),
                port=int(os.getenv('DB_PORT', '5432')),
                database=os.getenv('DB_NAME', '')
            ),
            aws=AWSConfig(
                access_key=os.getenv('AWS_ACCESS_KEY', ''),
                secret_key=os.getenv('AWS_SECRET_KEY', ''),
                s3_bucket=os.getenv('S3_BUCKET', 'sp500-financial-data'),
                redshift_uri=os.getenv('REDSHIFT_URI', '')
            ),
            env='prod'
        )

# Application config singleton
app_config: Config = None

def get_config(env: str = None) -> Config:
    """Get the application configuration"""
    global app_config
    if app_config is None:
        app_config = Config.load(env)
    return app_config
