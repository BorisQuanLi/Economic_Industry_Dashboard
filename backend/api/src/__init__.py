from flask import Flask
import simplejson as json
from flask import request
from datetime import datetime

import api.src.models as models
import api.src.db as db
import api.src.adapters.backend_utilities as utilities
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

    @app.route('/sub_sectors/')
    def find_all_sub_sectors():
        conn = db.get_db()
        cursor = conn.cursor()
        objs_list = db.find_all(models.SubIndustry, cursor)
        dicts_list = [obj.__dunict__ for obj in objs_list]
        return json.dumps(dicts_list)

    @app.route('/sub_sectors/search')
    def search_sub_sectors():
        """
        url format:
        http://127.0.0.1:5000/sub_sectors/search?sub_sector_name=Xyz&financial_indicator=revenue
        """
        conn, cursor, sub_sector_name, financial_indicator = utilities.company_performance_query_tools()
        conn = db.get_db()
        cursor = conn.cursor()
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
        # TBD, to the end of this function
        conn = db.get_db()
        cursor = conn.cursor()
        params = dict(request.args)
        sub_industry_name = params['sub_industry']
        # generate a list of companies in the same sub_industry
        companies_info = [company.__dict__ for company 
                                    in db.find_companies_by_sub_industry_name(models.Company, sub_industry_name, cursor)]
        """
        generate of list of quarterly performance numbers
        """
        sub_industry_info = {}
        sub_industry_info['companies'] = companies_info
        # sub_industry_info['quarterly numbers'] = quarterly_numbers_history
        return json.dumps(sub_industry_info)

    @app.route('/sub_sectors/<sub_sector_name>')
    def company_financial_performance(sub_industry_name):
        conn, cursor, financial_indicator = utilities.financial_performance_query_tools()
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
    

    @app.route('/sectors/search')
    def sub_industries_within_sector():
        """
        url format:
        http://127.0.0.1:5000/sectors/search?sector_name=Energy&financial_indicator=revenue
        """
        conn, cursor, sector_name, financial_indicator = utilities.sub_sector_performance_query_tools()
        if sector_name == 'all_sectors':
            conn = db.get_db()
            cursor = conn.cursor()
            sector_names = MixinSectorPricePE.get_all_sector_names(models.SubIndustry, cursor)
            return json.dumps({'sector_names': sector_names}, default=str)
        else:
            if financial_indicator in ['revenue', 'net_income', 'earnings_per_share', 'profit_margin']:
                historical_financials_json_dicts = (models.SubIndustry.
                                                        find_sub_industry_avg_quarterly_financials(sector_name, financial_indicator, cursor))
            elif financial_indicator in ['closing_price', 'price_earnings_ratio']:
                historical_financials_json_dicts = (models.SubIndustry.
                                                        find_sub_industry_avg_quarterly_price_pe(sector_name, financial_indicator, cursor))
            else:
                historical_financials_json_dicts = {'Please enter the name of a financial indicator.'}
            return json.dumps(historical_financials_json_dicts, default = str)
            

    @app.route('/sectors')
    def sector_avg_financial_performance():
        """
        url: /sectors?financial_indicator={financial_indicator_name}
        returns the quarterly average, over the most recent 8 quarters, of the financial indicator of all the sectors
        """
        conn, cursor, financial_indicator = utilities.financial_performance_query_tools()
        if financial_indicator in ['revenue', 'net_income', 'earnings_per_share', 'profit_margin']:
            historical_financials_json_dicts = (models.SubIndustry.
                                                        find_sector_avg_quarterly_financials(financial_indicator, cursor))
        elif financial_indicator in ['closing_price', 'price_earnings_ratio']:
            historical_financials_json_dicts = (models.SubIndustry.
                                                        find_sector_avg_price_pe(financial_indicator, cursor))
        else:
            historical_financials_json_dicts = {'Please enter the name of a financial indicator.'}
            breakpoint()
        return json.dumps(historical_financials_json_dicts, default = str)

    @app.route('/sectors/<sector_name>')
    def get_sub_sector_names_within_sector(sector_name):
        conn = db.get_db()
        cursor = conn.cursor()
        sub_sector_names = MixinSubSectorPricePE.get_sub_sector_names_of_sector(models.SubIndustry, sector_name, cursor) 
        return json.dumps({'sub_sector_names': sub_sector_names}, default=str)

    return app

    """
    To be implemented after the Company.search() method is worked out.

    @app.route('/companies/search')
    def search_companies():
        conn = db.get_db()
        cursor = conn.cursor()

        params = dict(request.args)
        venues = models.Company.search(params, cursor)
        venue_dicts = [venue.to_json(cursor) for venue in venues]
        return json.dumps(venue_dicts, default = str)
    
    
    @app.route('/companies')
    def companies():
        conn = db.get_db()
        cursor = conn.cursor()
        companies = db.find_all(models.Company, cursor)
        company_dicts = [company.__dict__ for company in companies]
        return json.dumps(company_dicts, default = str)

    @app.route('/companies/<id>')
    def company(id):
        conn = db.get_db()
        cursor = conn.cursor()
        company = db.find(models.Company, id, cursor)
        return json.dumps(company.__dict__, default = str)

    @app.route('/companies/company_overview/<ticker>') 
    def company_overview_by_ticker(ticker):
        conn = db.get_db()
        cursor = conn.cursor()
        company = db.find_by_ticker(models.Company, ticker, cursor)
        ic_pe_json = company.to_quarterly_financials_json(db.cursor)
        return json.dumps(ic_pe_json, default = str)

    @app.route('/companies/company_overview/search') # see code above
    def find_company_by_name():
        conn = db.get_db()
        cursor = conn.cursor()
        # params = dict(request.args)
        company_names = request.args.getlist('company_name')
        jsons_list = get_jsons(company_names, cursor)
        return json.dumps(jsons_list, default = str)

    def get_jsons(company_names:list, cursor):
        json_list = []
        for company_name in company_names:
            company = db.find_by_name(models.Company, company_name, cursor)
            ic_pe_json = company.to_quarterly_financials_json(db.cursor)
            json_list.append(ic_pe_json)
        return json_list

    @app.route('/companies/latest_quarter_company_overview/<ticker>')
    def latest_quarter_company_overview(ticker):
        conn = db.get_db()
        cursor = conn.cursor()
        company = db.find_by_ticker(models.Company, ticker, cursor)
        ic_pe_json = company.to_quarterly_reports_prices_pe_json_by_ticker(db.cursor)
        
        latest_quarterly_report = ic_pe_json['History of quarterly financials'][0]
        ic_pe_json["Latest quarter's financials"] = latest_quarterly_report
        ic_pe_json.pop('History of quarterly financials')

        latest_price_pe = ic_pe_json['History of quarterly Closing Price and Price to Earnings ratios'][0]
        ic_pe_json["Latest quarter's stock price and price-to-earnings ratio"] = latest_price_pe
        ic_pe_json.pop('History of quarterly Closing Price and Price to Earnings ratios')

        return json.dumps(ic_pe_json, default = str)


    @app.route('/companies/quarterly_reports_by_company/<ticker>')
    def quarterly_reports_by_ticker(ticker):
        conn = db.get_db()
        cursor = conn.cursor()
        quarterly_reports_objs = db.find_quarterly_reports_by_ticker(models.QuarterlyReport, ticker, cursor)
        quarterly_reports_dicts = [report.__dict__ 
                                            for report in quarterly_reports_objs]
        return json.dumps(quarterly_reports_dicts, default = str)

    @app.route('/companies/latest_quarterly_result_by_company/<ticker>')
    def latest_quarterly_result_company(ticker):
        conn = db.get_db()
        cursor = conn.cursor()
        quarterly_reports_objs = db.find_quarterly_reports_by_ticker(models.QuarterlyReport, ticker, cursor)
        latest_quarterly_report_obj = quarterly_reports_objs[0]
        return json.dumps(
                    latest_quarterly_report_obj.__dict__, default = str)
                    
    # develop all_quarterly_result
    
    @app.route('/companies/price_pe/<ticker>')
    def price_pe_company(ticker):
        conn = db.get_db()
        cursor = conn.cursor()
        company_price_pe = db.find_latest_company_price_pe_by_ticker(
            models.PricePE, ticker, cursor)
        company_price_pe = company_price_pe.to_latest_pe_json(cursor)
        return json.dumps(company_price_pe, default = str)
    """