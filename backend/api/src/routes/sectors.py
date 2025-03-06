from flask import Blueprint, jsonify, request
import simplejson as json
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

# ... move other sector-related routes here ...
