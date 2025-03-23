"""Health check endpoints."""
from flask import Blueprint, jsonify, current_app
import datetime

health_bp = Blueprint('health', __name__, url_prefix='/health')

@health_bp.route('', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.datetime.now().isoformat(),
        'service': 'Economic Industry Dashboard API'
    })

@health_bp.route('/services', methods=['GET'])
def service_health():
    """Check the health of all services."""
    services = current_app.config.get('services', {})
    
    service_status = {}
    for name, service in services.items():
        # Check if service is available
        service_status[name] = 'available' if service else 'unavailable'
    
    return jsonify({
        'status': 'ok' if all(s == 'available' for s in service_status.values()) else 'degraded',
        'services': service_status,
        'timestamp': datetime.datetime.now().isoformat()
    })
