from flask import Blueprint, request
import simplejson as json
import etl_service.src.models as models
import etl_service.src.db as db
from backend.api.src.adapters.backend_utilities import financial_performance_query_tools

sector_bp = Blueprint('sector_bp', __name__)

@sector_bp.route('/sectors/')
def sector_avg_financial_performance():
    """
    url parameter format: f'/sectors/?financial_indicator={financial_indicator_name}'
    returns the quarterly average, over the most recent 8 quarters, of the financial indicator of each and every sector
    """
    conn, cursor, financial_indicator = financial_performance_query_tools()
    historical_financials_json_dicts = get_historical_financials_json(financial_indicator, cursor)
    return json.dumps(historical_financials_json_dicts, default = str)

def get_historical_financials_json(financial_indicator, cursor):
    if financial_indicator in ['revenue', 'net_income', 'earnings_per_share', 'profit_margin']:
        historical_financials_json_dicts = (models.SubIndustry.
                                                    find_avg_quarterly_financials_by_sector(financial_indicator, cursor))
    elif financial_indicator in ['closing_price', 'price_earnings_ratio']:
        historical_financials_json_dicts = (models.SubIndustry.
                                                    find_sector_avg_price_pe(financial_indicator, cursor))
    # needs to handle dropdown menu selection of 'Done. Continue to the sub-Sector level.'
    else:
        historical_financials_json_dicts = 'Please enter the name of a financial_indicator, such as revenue, net_income.'
    return historical_financials_json_dicts
