"""
Backend Flask Application Entry Point for Economic Industry Dashboard

This module serves as the main entry point for the backend Flask web service.
It initializes and runs the web application with the following responsibilities:

1. Application Setup:
   - Creates Flask application via factory pattern
   - Configures development settings
   - Sets up logging

2. Service Initialization:
   - Initializes core services (IndustryAnalyzer)
   - Manages service dependencies

3. Application Launch:
   - Runs the Flask development server
   - Configures debug mode based on environment

Usage:
    python run.py
"""

import logging
from .factory import create_app  # relative import since we're in webservice package
from .services.industry_analysis import IndustryAnalyzer  # relative import
from backend.etl.load.data_persistence.base import DevelopmentConfig  # Updated import path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def init_services():
    """
    Initialize core services.

    Returns:
        dict: Dictionary of initialized services
    """
    # Create database connection
    from etl.load.data_persistence.local_postgres import LocalPostgresRepository
    from etl.load.data_persistence.base import DevelopmentConfig
    
    config = DevelopmentConfig()
    db_repo = LocalPostgresRepository(config.database_settings)
    
    # Pass db connection to IndustryAnalyzer
    analyzer = IndustryAnalyzer(db_repo)

    return {
        'industry_analyzer': analyzer,
        'db_connection': db_repo
    }

if __name__ == '__main__':
    config = DevelopmentConfig()  # Required for create_app() and app.run()
    services = init_services()
    app = create_app(config, services)  # uses config here
    logger.info('Starting Economic Industry Dashboard web service')
    app.run(debug=config.DEBUG)  # uses config.DEBUG here