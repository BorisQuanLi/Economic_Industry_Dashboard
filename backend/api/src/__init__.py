from flask import Flask
import simplejson as json
from flask import request
from datetime import datetime

import api.src.models as models
import api.src.db as db
from api.src.adapters.backend_utilities import (financial_performance_query_tools, 
                    sub_sector_performance_query_tools, company_performance_query_tools)
from api.src.models.queries.query_sector_price_pe import MixinSectorPricePE
from api.src.models.queries.query_sub_sector_price_pe import MixinSubSectorPricePE
from api.src.models.queries.query_company_financials_history import MixinCompanyFinancials
from api.src.models.queries.query_company_price_pe_history import MixinCompanyPricePE
from api.src.models.queries.sql_query_strings import companies_within_sub_sector_str, sub_sector_names_in_sector_query_str
from settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER, DEBUG, TESTING

def create_app(database='investment_analysis', testing=False, debug=True):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    
    # connect to the local computer's Postgres
    app.config.from_mapping(
        DB_USER = 'postgres',
        DB_NAME = database,
        DB_PASSWORD = 'postgres',
        DB_HOST = '127.0.0.1',
        DEBUG = DEBUG,
        TESTING = TESTING
    )

    """
    # connect to AWS RDS postgres
    app.config.from_mapping(
        DB_USER = DB_USER,
        DB_NAME = DB_NAME,
        DB_PASSWORD = db.DB_PASSWORD,
        DB_HOST = DB_HOST,
        DEBUG = DEBUG,
        TESTING = TESTING
    )
    """

    @app.route('/')
    def root_url():
        return 'Welcome to the Economic Analysis api, through the prism of the S&P 500 stocks performance.'

    @app.route('/sectors/')
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

    @app.route('/sectors/search')
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
       
    @app.route('/sub_sectors/search')
    def search_sub_sectors():
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
        
    @app.route('/sub_sectors/<sub_industry_name>')
    def company_financial_performance(sub_industry_name):
        conn, cursor, financial_indicator = financial_performance_query_tools()
        if sub_industry_name == 'all_sub_industries':
            sector_name = financial_indicator
            sub_industry_names = MixinCompanyFinancialsPricePE.get_all_sub_sector_names_in_sector(models.Company, sector_name, cursor)
            return json.dumps({'sub_industry_names': sub_industry_names}, default=str)
        else:
            if financial_indicator in ['revenue', 'net_income', 'earnings_per_share', 'profit_margin']:
                historical_financials_json_dicts = (models.SubIndustry.
                                                        find_companies_quarterly_financials(sub_sector_name, financial_indicator, cursor))
            elif financial_indicator in ['closing_price', 'price_earnings_ratio']:
                historical_financials_json_dicts = (models.SubIndustry.
                                                        find_company_quarterly_price_pe(sector_name, financial_indicator, cursor))
            else:
                historical_financials_json_dicts = {'Please enter the name of a financial indicator.'}
            return json.dumps(historical_financials_json_dicts, default = str)
    
    @app.route('/sectors/<sector_name>')
    def get_sub_sector_names_within_sector(sector_name):
        conn = db.get_db()
        cursor = conn.cursor()
        sub_sector_names = MixinSubSectorPricePE.get_sub_sector_names_of_sector(models.SubIndustry, sector_name, cursor) 
        return json.dumps({'sub_sector_names': sub_sector_names}, default=str)     

    return app
