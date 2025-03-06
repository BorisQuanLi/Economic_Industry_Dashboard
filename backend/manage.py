#!/usr/bin/env python3
import click
import logging
from typing import Optional
from api.src import create_app
from api.src.config import DevelopmentConfig, ProductionConfig, TestingConfig
from api.src.db import get_db, init_db
from api.src.adapters.data_ingestion_adapters import BuildSP500Companies, BuildQuarterlyReportsPricesPE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_config(env: str):
    configs = {
        'dev': DevelopmentConfig,
        'prod': ProductionConfig,
        'test': TestingConfig
    }
    return configs.get(env, DevelopmentConfig)

@click.group()
def cli():
    """SP500 Dashboard management CLI"""
    pass

@cli.command()
@click.option('--env', default='dev', help='Environment (dev/prod/test)')
def run(env: str):
    """Run the Flask application server."""
    config = get_config(env)
    app = create_app(config)
    logger.info(f'Starting application in {env} mode')
    app.run(debug=config.DEBUG)

@cli.command()
@click.option('--sector', help='Optional: Process specific sector only')
def build_data(sector: Optional[str] = None):
    """Build or update the database with S&P 500 company data."""
    try:
        logger.info('Starting data build process')
        
        # Initialize database connection
        conn = get_db()
        cursor = conn.cursor()

        # Build company data
        logger.info('Building S&P 500 companies data')
        builder = BuildSP500Companies()
        builder.run()

        # Build financial reports and price data
        if sector:
            logger.info(f'Building quarterly data for sector: {sector}')
            reports_builder = BuildQuarterlyReportsPricesPE(conn, cursor)
            reports_builder.run(sector)
        
        logger.info('Data build process completed successfully')
        
    except Exception as e:
        logger.error(f'Error during data build: {str(e)}')
        raise click.ClickException(str(e))
    finally:
        cursor.close()
        conn.close()

@cli.command()
@click.option('--env', default='dev', help='Environment (dev/prod/test)')
def init_db(env: str):
    """Initialize the database."""
    try:
        logger.info(f'Initializing database for {env} environment')
        config = get_config(env)
        app = create_app(config)
        with app.app_context():
            # Import and run database initialization code
            from api.src.db import init_db
            init_db(app)
        logger.info('Database initialization completed')
    except Exception as e:
        logger.error(f'Database initialization failed: {str(e)}')
        raise click.ClickException(str(e))

if __name__ == '__main__':
    cli()
