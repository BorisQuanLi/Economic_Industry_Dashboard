"""Sector-related endpoints."""
from flask import Blueprint, jsonify, current_app, request, abort
import simplejson as json
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Create a mock SubIndustry class in case imports fail
class MockSubIndustry:
    @staticmethod
    def find_avg_quarterly_financials_by_sector(*args, **kwargs):
        return []
    
    @staticmethod
    def find_sector_avg_price_pe(*args, **kwargs):
        return []

# Mock function for financial_performance_query_tools
def mock_financial_performance_query_tools(*args, **kwargs):
    return None, None, 'revenue'

# Try to import real implementations
try:
    # Try relative imports first
    from ...etl.transform.models.industry.sector import SubIndustry
    from ...etl.transform.adapters.imports import financial_performance_query_tools
    logger.info("Successfully imported ETL modules")
except ImportError as e:
    # Fall back to absolute imports
    try:
        from backend.etl.transform.models.industry.sector import SubIndustry
        from backend.etl.transform.adapters.imports import financial_performance_query_tools
        logger.info("Successfully imported ETL modules using absolute imports")
    except ImportError as e:
        # Try one more import path (new structure)
        try:
            from backend.etl.etl_pipeline.transform.models.industry.sector import SubIndustry
            from backend.etl.etl_pipeline.transform.adapters.imports import financial_performance_query_tools
            logger.info("Successfully imported ETL modules from etl_pipeline structure")
        except ImportError as e2:
            # If all imports fail, use mocks
            logger.warning(f"Using mock implementations due to import error: {str(e)} and {str(e2)}")
            SubIndustry = MockSubIndustry
            financial_performance_query_tools = mock_financial_performance_query_tools

# Try to import the query service with proper error handling
try:
    from ..services.database.query_service import QueryService
    logger.info("Successfully imported query service")
except ImportError as e:
    # Try alternative import paths
    try:
        from backend.webservice.services.database.query_service import QueryService
        logger.info("Successfully imported query service using absolute import")
    except ImportError as e2:
        logger.error(f"Error importing query service: {str(e)} and then {str(e2)}")
        # Create a mock QueryService if needed
        class MockQueryService:
            def __getattr__(self, name):
                return lambda *args, **kwargs: []
    
        QueryService = MockQueryService

sector_bp = Blueprint('sectors', __name__, url_prefix='/sectors')

@sector_bp.route('/')
def sector_avg_financial_performance():
    try:
        conn, cursor, financial_indicator = financial_performance_query_tools()
        
        if financial_indicator in ['revenue', 'net_income', 'earnings_per_share', 'profit_margin']:
            data = SubIndustry.find_avg_quarterly_financials_by_sector(financial_indicator, cursor)
        elif financial_indicator in ['closing_price', 'price_earnings_ratio']:
            data = SubIndustry.find_sector_avg_price_pe(financial_indicator, cursor)
        else:
            return jsonify(error='Invalid financial indicator'), 400
            
        return json.dumps(data, default=str)
    except Exception as e:
        logger.error(f"Error in sector_avg_financial_performance: {str(e)}")
        return jsonify(error=str(e)), 500

@sector_bp.route('', methods=['GET'])
def get_sectors():
    """Get all sectors."""
    analyzer = current_app.config.get('services', {}).get('industry_analyzer')
    if not analyzer:
        return jsonify({'error': 'Service not available'}), 503
        
    sectors = analyzer.get_sectors()
    return jsonify({'sectors': sectors})

@sector_bp.route('/<int:sector_id>', methods=['GET'])
def get_sector(sector_id):
    """Get sector by ID with detailed metrics."""
    analyzer = current_app.config.get('services', {}).get('industry_analyzer')
    if not analyzer:
        return jsonify({'error': 'Service not available'}), 503
    
    try:
        sector_data = analyzer.get_sector_data(sector_id)
        if not sector_data:
            return jsonify({'error': 'Sector not found'}), 404
            
        return jsonify(sector_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sector_bp.route('/<int:sector_id>/metrics', methods=['GET'])
def get_sector_metrics(sector_id):
    """Get financial metrics for a sector."""
    analyzer = current_app.config.get('services', {}).get('industry_analyzer')
    if not analyzer:
        return jsonify({'error': 'Service not available'}), 503
    
    # Get optional query parameters
    time_period = request.args.get('period', 'quarterly')  # quarterly, annual
    metrics = request.args.get('metrics', 'all')  # revenue, profit, pe_ratio, all
    
    try:
        metrics_data = analyzer.get_sector_metrics(
            sector_id, 
            time_period=time_period,
            metrics=metrics.split(',') if metrics != 'all' else None
        )
        if not metrics_data:
            return jsonify({'error': 'Sector metrics not found'}), 404
            
        return jsonify(metrics_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@sector_bp.route('/<int:sector_id>/sub_industries', methods=['GET'])
def get_sector_sub_industries(sector_id):
    """Get all sub-industries in a sector."""
    analyzer = current_app.config.get('services', {}).get('industry_analyzer')
    if not analyzer:
        return jsonify({'error': 'Service not available'}), 503
    
    try:
        sub_industries = analyzer.get_sub_industries_by_sector(sector_id)
        if sub_industries is None:
            return jsonify({'error': 'Sector not found'}), 404
            
        return jsonify({'sub_industries': sub_industries})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
