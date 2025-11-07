from flask import Blueprint, request
import simplejson as json
import api.src.models as models
import api.src.db as db
from api.src.adapters.backend_utilities import (financial_performance_query_tools, 
                    sub_sector_performance_query_tools)
from api.src.models.queries.query_sector_price_pe import MixinSectorPricePE
from api.src.models.queries.query_sub_sector_price_pe import MixinSubSectorPricePE

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

@sector_bp.route('/sectors/search')
def sub_industries_within_sector():
    """
    url parameter format example: /sectors/search?sector_name=Energy&financial_indicator=revenue
    returns the quarterly average, over the most recent 8 quarters, of the selected financial indicator and sector
    """
    conn, cursor, sector_name, financial_indicator = sub_sector_performance_query_tools()
    if sector_name == 'all_sectors':        
        conn = db.get_db()
        cursor = conn.cursor()
        sector_names = MixinSectorPricePE.get_all_sector_names(models.SubIndustry, cursor)
        return {'all_sector_names': sector_names}
    else:
        if financial_indicator in ['revenue', 'net_income', 'earnings_per_share', 'profit_margin']:
            historical_financials_json_dicts = (models.SubIndustry.
                                                    find_avg_quarterly_financials_by_sub_industry(sector_name, financial_indicator, cursor))
        elif financial_indicator in ['closing_price', 'price_earnings_ratio']:
            historical_financials_json_dicts = (models.SubIndustry.
                                                    find_sub_industry_avg_quarterly_price_pe(sector_name, financial_indicator, cursor))
        else:
            historical_financials_json_dicts = {'Please enter the name of a financial indicator.'}
        return json.dumps(historical_financials_json_dicts, default = str)

@sector_bp.route('/sectors/<sector_name>')
def get_sub_sector_names_within_sector(sector_name):
    conn = db.get_db()
    cursor = conn.cursor()
    sub_sector_names = MixinSubSectorPricePE.get_sub_sector_names_of_sector(models.SubIndustry, sector_name, cursor) 
    return json.dumps({'sub_sector_names': sub_sector_names}, default=str)
