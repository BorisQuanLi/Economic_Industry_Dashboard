"""Sector-related endpoints."""
from flask import Blueprint, jsonify, current_app, request, abort
import simplejson as json
from typing import Dict, List, Any
from etl.transform.models.industry.sector import SubIndustry
from etl.transform.adapters.imports import financial_performance_query_tools

sector_bp = Blueprint('sectors', __name__, url_prefix='/sectors')

@sector_bp.route('/')
def sector_avg_financial_performance():
    conn, cursor, financial_indicator = financial_performance_query_tools()
    
    if financial_indicator in ['revenue', 'net_income', 'earnings_per_share', 'profit_margin']:
        data = SubIndustry.find_avg_quarterly_financials_by_sector(financial_indicator, cursor)
    elif financial_indicator in ['closing_price', 'price_earnings_ratio']:
        data = SubIndustry.find_sector_avg_price_pe(financial_indicator, cursor)
    else:
        return jsonify(error='Invalid financial indicator'), 400
        
    return json.dumps(data, default=str)

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
