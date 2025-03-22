"""Routes module for the API."""

from flask import Blueprint, jsonify, current_app

# Create a Blueprint for API routes
routes = Blueprint('api', __name__)

@routes.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'sector-analytics-api'
    })

@routes.route('/sectors', methods=['GET'])
def get_sectors():
    """Get all sectors."""
    analyzer = current_app.config.get('services', {}).get('industry_analyzer')
    if not analyzer:
        return jsonify({'error': 'Service not available'}), 503
        
    sectors = analyzer.get_sectors()
    return jsonify({'sectors': sectors})
