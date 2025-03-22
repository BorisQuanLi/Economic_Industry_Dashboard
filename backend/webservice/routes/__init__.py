"""API routes package."""
from flask import Blueprint

# Create main API blueprint 
api = Blueprint('api', __name__, url_prefix='/api/v1')

# Import and register resource blueprints
from .sectors import sector_bp
from .companies import company_bp
from .health import health_bp

api.register_blueprint(sector_bp)
api.register_blueprint(company_bp)
api.register_blueprint(health_bp)

# Export the combined blueprint
routes = api
