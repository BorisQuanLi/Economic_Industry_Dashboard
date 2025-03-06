from flask import Flask
from .config import load_config
from .routes.sectors import sectors_bp

def create_app(env: str = 'dev') -> Flask:
    """Create Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config = load_config(env)
    app.config.from_object(config)
    
    # Register blueprints
    app.register_blueprint(sectors_bp, url_prefix='/api/v1')
    
    return app
