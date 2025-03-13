"""
Core business logic and web service for the Economic Industry Dashboard.
"""
from flask import Flask
from flask_cors import CORS
from etl.transform.models import Company, SectorMetrics, SubSectorMetrics
from .services import DataProcessor, AnalysisService
from .routes import web

def create_app(config=None, services=None):
    """Create Flask application with all routes and services."""
    app = Flask(__name__)
    CORS(app)
    
    if config:
        app.config.from_object(config)
    
    app.register_blueprint(web, url_prefix='/api')
    return app