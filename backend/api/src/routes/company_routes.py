from flask import Blueprint, request
import simplejson as json
import api.src.models as models
import api.src.db as db
from api.src.adapters.backend_utilities import company_performance_query_tools, financial_performance_query_tools
from api.src.models.queries.query_sub_sector_price_pe import MixinSubSectorPricePE
from api.src.models.queries.query_company_price_pe_history import MixinCompanyFinancialsPricePE

company_bp = Blueprint('company_bp', __name__)

@company_bp.route('/companies/search')
def search_companies():
    conn, cursor, sub_sector_name, financial_indicator = company_performance_query_tools()
    if sub_sector_name == 'all_sub_sectors':
        sector_name = financial_indicator
        sub_sector_names = MixinSubSectorPricePE.get_sub_sector_names_of_sector(models.SubIndustry, sector_name, cursor)
        return json.dumps({'sub_sector_names': sub_sector_names}, default=str)
    else:
        if financial_indicator in ['revenue', 'net_income', 'earnings_per_share', 'profit_margin']:
            historical_financials_json_dicts = (models.Company.
                                                        find_companies_quarterly_financials(sub_sector_name, financial_indicator, cursor))
        elif financial_indicator in ['closing_price', 'price_earnings_ratio']:
            historical_financials_json_dicts = (models.Company.find_company_quarterly_price_pe(sub_sector_name, financial_indicator, cursor))
        else:
            historical_financials_json_dicts = {'Please enter the name of a financial indicator.'}
        return json.dumps(historical_financials_json_dicts, default = str)

@company_bp.route('/sub_sectors/<sub_industry_name>/companies')
def company_financial_performance(sub_industry_name):
    conn, cursor, financial_indicator = financial_performance_query_tools()
    if sub_industry_name == 'all_sub_industries':
        sector_name = financial_indicator
        sub_industry_names = MixinCompanyFinancialsPricePE.get_all_sub_sector_names_in_sector(models.Company, sector_name, cursor)
        return json.dumps({'sub_industry_names': sub_industry_names}, default=str)
    else:
        if financial_indicator in ['revenue', 'net_income', 'earnings_per_share', 'profit_margin']:
            historical_financials_json_dicts = (models.Company.
                                                    find_companies_quarterly_financials(sub_industry_name, financial_indicator, cursor))
        elif financial_indicator in ['closing_price', 'price_earnings_ratio']:
            historical_financials_json_dicts = (models.Company.
                                                    find_company_quarterly_price_pe(sub_industry_name, financial_indicator, cursor))
        else:
            historical_financials_json_dicts = {'Please enter the name of a financial indicator.'}
        return json.dumps(historical_financials_json_dicts, default = str)
