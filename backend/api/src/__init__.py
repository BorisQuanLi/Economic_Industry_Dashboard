from flask import Flask
from .config import load_config
from .routes.sectors import sectors_bp
from .adapters.wiki_page_client import get_sp500_wiki_data
from api.src.db import init_app

__all__ = ['get_sp500_wiki_data']

def create_app(config_object=None) -> Flask:
    """Create Flask application"""
    app = Flask(__name__)

    if config_object:
        app.config.from_object(config_object)

    # Initialize database
    init_app(app)

    # Register blueprints
    app.register_blueprint(sectors_bp, url_prefix='/api/v1')

    return app
