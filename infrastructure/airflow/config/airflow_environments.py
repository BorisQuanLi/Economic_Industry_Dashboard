"""
Configuration settings for different Airflow environments.
"""
from typing import Dict, Any

# Base configuration class
class AirflowConfig:
    """Base configuration for Airflow environments."""
    # General settings
    OWNER = "data-engineering-team"
    EMAIL_ON_FAILURE = True
    EMAIL_ON_RETRY = False
    RETRIES = 1
    RETRY_DELAY_MINUTES = 5
    
    # Database settings
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_NAME = "economic_dashboard"
    DB_USER = "airflow"
    DB_PASSWORD = "changeme"  # Always override this in deployment
    
    # S3 settings
    S3_BUCKET = "economic-dashboard-data"
    
    # Default schedule intervals
    DAILY_SCHEDULE = "0 1 * * *"  # 1 AM daily
    WEEKLY_SCHEDULE = "0 2 * * 1"  # 2 AM on Mondays
    
    @classmethod
    def get_db_connection_string(cls) -> str:
        """Get database connection string."""
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
    
    @classmethod
    def get_connection_dict(cls) -> Dict[str, Any]:
        """Get connection dictionary for direct psycopg2 connection."""
        return {
            "host": cls.DB_HOST,
            "port": cls.DB_PORT,
            "database": cls.DB_NAME,
            "user": cls.DB_USER,
            "password": cls.DB_PASSWORD
        }

# Development environment configuration
class DevConfig(AirflowConfig):
    """Development environment configuration."""
    EMAIL_ON_FAILURE = False
    S3_BUCKET = "economic-dashboard-data-dev"
    
    # Override with development settings
    DB_HOST = "localhost"
    DB_NAME = "economic_dashboard_dev"
    DB_USER = "dev_user"
    DB_PASSWORD = "dev_password"

# Production environment configuration
class ProdConfig(AirflowConfig):
    """Production environment configuration."""
    RETRIES = 3
    RETRY_DELAY_MINUTES = 10
    S3_BUCKET = "economic-dashboard-data-prod"
    
    # Should be set via environment variables in production
    DB_HOST = "production-db-host"
    DB_NAME = "economic_dashboard_prod"
    DB_USER = "prod_user"
    DB_PASSWORD = "CHANGE_ME_IN_PRODUCTION"  # Should be set via environment variables

# Choose configuration based on environment
def get_config(environment: str = "dev") -> AirflowConfig:
    """
    Get configuration for the specified environment.
    
    Args:
        environment (str): Environment name (dev, prod)
        
    Returns:
        AirflowConfig: Configuration object for the specified environment
    """
    if environment.lower() == "prod":
        return ProdConfig
    return DevConfig
