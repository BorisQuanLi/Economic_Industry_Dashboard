from flask import Flask
from .config import load_config
from .routes.sectors import sectors_bp

def create_app(config_object=None) -> Flask:
    """Create Flask application"""
    app = Flask(__name__)
    
    if config_object:
        app.config.from_object(config_object)
    
    from .db import init_app
    init_app(app)
    
    # Register blueprints
    app.register_blueprint(sectors_bp, url_prefix='/api/v1')
    
    return app
