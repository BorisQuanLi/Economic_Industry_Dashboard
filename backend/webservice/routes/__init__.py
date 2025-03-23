"""
Routes package initialization
"""
from flask import Blueprint

# Create main API blueprint 
api = Blueprint('api', __name__, url_prefix='/api/v1')

# Import and register resource blueprints
try:
    from .sectors import sector_bp
    from .companies import company_bp
    from .health import health_bp

    api.register_blueprint(sector_bp)
    api.register_blueprint(company_bp)
    api.register_blueprint(health_bp)
except ImportError as e:
    import logging
    logging.getLogger(__name__).error(f"Error importing route modules: {str(e)}")
    # Creating empty blueprints to avoid errors if modules aren't available
    sector_bp = Blueprint('sectors', __name__, url_prefix='/sectors')
    company_bp = Blueprint('companies', __name__, url_prefix='/companies')
    health_bp = Blueprint('health', __name__, url_prefix='/health')
    
    api.register_blueprint(sector_bp)
    api.register_blueprint(company_bp)
    api.register_blueprint(health_bp)

# Export the combined blueprint
routes = api
blueprint = api
