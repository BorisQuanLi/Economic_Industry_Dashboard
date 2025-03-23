"""Company-related endpoints."""
from flask import Blueprint, jsonify, current_app, request, abort
import simplejson as json
from typing import Dict, List, Any

company_bp = Blueprint('companies', __name__, url_prefix='/companies')

@company_bp.route('', methods=['GET'])
def get_companies():
    """Get all companies or filter by sector."""
    # Get query parameters
    sector_id = request.args.get('sector_id', type=int)
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    analyzer = current_app.config.get('services', {}).get('industry_analyzer')
    if not analyzer:
        return jsonify({'error': 'Service not available'}), 503
    
    try:
        if sector_id:
            companies = analyzer.get_companies_by_sector(sector_id, limit=limit, offset=offset)
        else:
            companies = analyzer.get_companies(limit=limit, offset=offset)
            
        return jsonify({'companies': companies, 'count': len(companies)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/<string:ticker>', methods=['GET'])
def get_company(ticker):
    """Get company details by ticker symbol."""
    analyzer = current_app.config.get('services', {}).get('industry_analyzer')
    if not analyzer:
        return jsonify({'error': 'Service not available'}), 503
    
    try:
        company_data = analyzer.get_company_data(ticker)
        if not company_data:
            return jsonify({'error': 'Company not found'}), 404
            
        return jsonify(company_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/<string:ticker>/financials', methods=['GET'])
def get_company_financials(ticker):
    """Get financial data for a company."""
    # Get query parameters
    period = request.args.get('period', 'quarterly')  # quarterly, annual
    metrics = request.args.get('metrics', 'all')
    limit = request.args.get('limit', 20, type=int)
    
    query_service = current_app.config.get('services', {}).get('query_service')
    if not query_service:
        return jsonify({'error': 'Service not available'}), 503
    
    try:
        financials = query_service.get_company_financials(ticker, limit=limit)
        if not financials:
            return jsonify({'error': 'No financial data found for company'}), 404
            
        return jsonify({'financials': financials})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/<string:ticker>/price_history', methods=['GET'])
def get_company_price_history(ticker):
    """Get price history for a company."""
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = request.args.get('limit', 100, type=int)
    
    query_service = current_app.config.get('services', {}).get('query_service')
    if not query_service:
        return jsonify({'error': 'Service not available'}), 503
    
    try:
        price_history = query_service.get_company_price_history(
            ticker,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        if not price_history:
            return jsonify({'error': 'No price history found for company'}), 404
            
        return jsonify({'price_history': price_history})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
