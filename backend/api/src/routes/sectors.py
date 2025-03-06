from flask import Blueprint, jsonify, request
import simplejson as json
from typing import Dict, List, Any
from api.src.models import SubIndustry
from api.src.adapters.backend_utilities import financial_performance_query_tools

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

@sector_bp.route('/sectors', methods=['GET'])
def get_sectors() -> Dict[str, List[str]]:
    """Get all sectors"""
    sectors = [
        'Technology',
        'Healthcare',
        'Finance',
        'Consumer Discretionary',
        'Industrial'
    ]
    return jsonify({'sectors': sectors})

@sector_bp.route('/sectors/<sector>/metrics', methods=['GET'])
def get_sector_metrics(sector: str) -> Dict[str, Any]:
    """Get financial metrics for a sector"""
    # Implementation will use the adapters to get and transform data
    return jsonify({
        'sector': sector,
        'metrics': {
            'avg_revenue': 0,
            'avg_profit_margin': 0,
            'total_market_cap': 0
        }
    })

# ... move other sector-related routes here ...
