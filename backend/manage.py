#!/usr/bin/env python3
import click
import logging
from typing import Optional
from data_sources.config import load_config  # Updated import path
from etl.pipeline import DataPipeline  # Update import path

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@click.group()
def cli():
    """Management CLI commands for ETL pipeline and database management."""
    pass

def get_config(env: str):
    """Get configuration for specified environment"""
    return load_config(env)

@cli.command()
@click.option('--env', default='dev', help='Environment (dev/prod/test)')
@click.option('--sector', help='Specific sector to process (optional)')
def etl(env: str, sector: Optional[str] = None):
    """Run ETL pipeline to fetch and process S&P 500 data."""
    config = get_config(env)
    pipeline = DataPipeline(config)
    
    if sector:
        logger.info(f'Running ETL pipeline for sector: {sector}')
        pipeline.process_sector(sector)
    else:
        logger.info('Running full ETL pipeline')
        pipeline.process_all()

@cli.command()
@click.option('--env', default='dev', help='Environment (dev/prod/test)')
def init_db(env: str):
    """Initialize database schema."""
    config = get_config(env)
    pipeline = DataPipeline(config)
    logger.info('Initializing database schema')
    pipeline.init_database()

if __name__ == '__main__':
    cli()
