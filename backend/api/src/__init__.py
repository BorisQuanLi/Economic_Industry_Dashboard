from flask import Flask
from api.src.config import DevelopmentConfig, TestingConfig, ProductionConfig

def create_app(config_class=DevelopmentConfig):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    from api.src.db import init_db
    init_db(app)

    # Register blueprints
    from api.src.routes import sector_bp, sub_sector_bp
    app.register_blueprint(sector_bp)
    app.register_blueprint(sub_sector_bp)

    @app.route('/')
    def root_url():
        return 'Welcome to the S&P 500 Financial Analytics API'

    return app
