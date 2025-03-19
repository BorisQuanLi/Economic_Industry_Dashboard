from flask import Flask, jsonify, request
import logging
from flask_cors import CORS

logger = logging.getLogger(__name__)

def register_routes(app, services):
    """Register routes with the Flask application."""
    # Initialize services if None
    if services is None:
        # Import here to avoid circular imports
        from webservice.services.industry_analysis import IndustryAnalyzer
        services = {
            "industry_analyzer": IndustryAnalyzer()
        }
    
    industry_analyzer = services["industry_analyzer"]

    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "ok"}), 200

    @app.route('/sectors', methods=['GET'])
    def list_sectors():
        """List available sectors."""
        try:
            sectors = industry_analyzer.get_sectors()
            return jsonify(sectors), 200
        except Exception as e:
            logger.error(f"Error listing sectors: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route('/sector_metrics', methods=['GET'])
    def get_sector_metrics():
        """Get metrics for a specific sector."""
        sector = request.args.get('sector')
        if not sector:
            return jsonify({"error": "Sector is required"}), 400
        try:
            metrics = industry_analyzer.get_sector_metrics(sector)
            return jsonify(metrics), 200
        except Exception as e:
            logger.error(f"Error getting sector metrics: {e}")
            return jsonify({"error": str(e)}), 500
