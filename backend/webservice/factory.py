"""
Application factory module

This module provides functions to create and configure the Flask application.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS

logger = logging.getLogger(__name__)

def create_app(config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Import routes
    try:
        # Use the routes module that combines all blueprint routes
        from .routes import routes as api_routes
        
        # Register blueprints
        app.register_blueprint(api_routes)
        logger.info("Registered routes blueprint")
    except Exception as e:
        logger.error(f"Error registering blueprints: {str(e)}")
    
    # Enable CORS
    CORS(app)
    
    # Configure the application
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev_key'),
        DEBUG=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true',
    )
    
    # Apply additional configuration if provided
    if config:
        app.config.update(config)
    
    # Apply configuration from environment-specific settings
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        try:
            from .config.production import Config
            app.config.from_object(Config)
            logger.info("Applied production configuration")
        except ImportError:
            logger.warning("Production config not found, using defaults")
    elif env == 'development':
        try:
            from .config.development import Config
            app.config.from_object(Config)
            logger.info("Applied development configuration")
        except ImportError:
            logger.warning("Development config not found, using defaults")
    
    # Initialize services
    try:
        _init_services(app)
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        # Add stub services as fallback
        app.config['services'] = {
            'query_service': None,
            'connection_service': None,
            'industry_analyzer': None
        }
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def _init_services(app):
    """Initialize application services."""
    try:
        from .services.service_factory import ServiceFactory
        
        # Create services
        services = {
            'query_service': ServiceFactory.get_query_service(),
            'connection_service': ServiceFactory.get_connection_service(),
            'industry_analyzer': ServiceFactory.get_sector_metrics(),
            'company_analyzer': ServiceFactory.get_company_metrics(),
            'data_processor': ServiceFactory.get_data_processor()
        }
        
        # Add services to app config
        app.config['services'] = services
        
        logger.info("Application services initialized")
    except ImportError as e:
        logger.error(f"Error importing service factory: {str(e)}")
        # Create a simple mock class
        class MockService:
            def __getattr__(self, name):
                return lambda *args, **kwargs: None
                
        # Add stub services
        app.config['services'] = {
            'query_service': MockService(),
            'connection_service': MockService(),
            'industry_analyzer': MockService(),
            'company_analyzer': MockService(),
            'data_processor': MockService()
        }
        logger.warning("Using stub services due to import error")

def register_error_handlers(app):
    """Register error handlers for the Flask app."""
    
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Resource not found'}, 404
        
    @app.errorhandler(500)
    def server_error(error):
        return {'error': 'Internal server error'}, 500
        
    @app.errorhandler(400)
    def bad_request(error):
        return {'error': 'Bad request'}, 400
        
    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Access forbidden'}, 403
