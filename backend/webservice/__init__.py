"""
Web Service Package for Economic Industry Dashboard

This package contains the Flask web application that serves the dashboard's data.
"""

from flask import Flask

def register_extensions(app):
    """Register Flask extensions."""
    # Import here to avoid circular imports
    from backend.etl.load.data_persistence.local_postgres import LocalPostgresRepository
    
    # Register database connection teardown
    app.teardown_appcontext(LocalPostgresRepository.close_db_in_context)
    
    return app

def init_app():
    """Initialize the web application."""
    from .factory import create_app
    from .run import init_services
    from backend.etl.config import get_config
    
    config = get_config()
    services = init_services()
    app = create_app(config, services)
    
    app = register_extensions(app)
    
    return app
