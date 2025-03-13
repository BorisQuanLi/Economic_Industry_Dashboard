"""Main entry point for the Economic Industry Dashboard web service."""
import logging
from app import create_app
from app.industry_analysis import IndustryAnalyzer
from data_sources.config import DevelopmentConfig

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def init_services(config):
    """Initialize core services."""
    analyzer = IndustryAnalyzer()
    return {"industry_analyzer": analyzer}

if __name__ == '__main__':
    config = DevelopmentConfig()
    services = init_services(config)
    app = create_app(config, services)
    logger.info('Starting Economic Industry Dashboard web service')
    app.run(debug=config.DEBUG)

