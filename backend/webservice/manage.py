"""
Command Line Interface for Economic Industry Dashboard Management

This module provides CLI commands for managing both the web service and ETL pipeline:

1. Web Service Management:
   - Database initialization
   - Service initialization
   - Application configuration

2. ETL Pipeline Management:
   - Process S&P 500 sectors data
   - Configure environment settings
   - Manage database schema

Usage:
    python manage.py --help          # Show available commands
    python manage.py init-db         # Initialize database
    python manage.py etl --env=dev   # Run ETL pipeline
    python manage.py etl --sector=Technology  # Process specific sector
"""

import click
import logging
from typing import Optional
from backend.webservice.run import init_services
from backend.webservice.factory import create_app
from backend.etl.load.data_persistence.base import DevelopmentConfig
from backend.etl.pipeline import DataPipeline

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@click.group()
def cli():
    """Management script for the Economic Industry Dashboard."""
    pass

@cli.command()
def init_db():
    """Initialize the web service database."""
    config = DevelopmentConfig()
    services = init_services()
    app = create_app(config, services)
    
    with app.app_context():
        # Initialize database here
        click.echo('Initialized the database.')

@cli.command()
@click.option('--env', default='dev', help='Environment (dev/prod/test)')
@click.option('--sector', help='Specific sector to process (optional)')
def etl(env: str, sector: Optional[str] = None):
    """Run ETL pipeline to fetch and process S&P 500 data."""
    config = DevelopmentConfig()  # Using DevelopmentConfig for now
    pipeline = DataPipeline(config)
    
    if sector:
        logger.info(f'Running ETL pipeline for sector: {sector}')
        pipeline.process_sector(sector)
    else:
        logger.info('Running full ETL pipeline')
        pipeline.process_all()

if __name__ == '__main__':
    cli()
