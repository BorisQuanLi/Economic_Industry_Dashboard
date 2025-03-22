from flask import Flask
from flask_cors import CORS

def create_app(config=None, services=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)

    if config:
        app.config.update(config.__dict__)

    # Store services in app config
    if services:
        app.config['services'] = services

    # Register routes
    from webservice.routes import routes as api_routes
    app.register_blueprint(api_routes)

    # Register error handlers
    register_error_handlers(app)

    return app

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
