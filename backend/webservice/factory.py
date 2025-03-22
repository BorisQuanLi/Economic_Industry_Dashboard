from flask import Flask
from flask_cors import CORS

def create_app(config=None, services=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    if config:
        app.config.update(config.__dict__)

    # Register routes
    from webservice.routes import routes as routes_blueprint
    app.register_blueprint(routes_blueprint)

    # Store services in app config
    if services:
        app.config['services'] = services

    return app
