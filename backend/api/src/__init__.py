from flask import Flask
import simplejson as json
from flask import request
from datetime import datetime

import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters
from settings import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER, DEBUG, TESTING

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    
    # connect to the local computer's Postgres
    app.config.from_mapping(
        DB_USER = 'postgres',
        DB_NAME = 'investment_analysis',
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
        return 'Welcome to the Stocks Performance api, through the prism of the S&P 500 Index components.'

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
        params = dict(request.args)
        company_name = params['company_name']
        company = db.find_by_name(models.Company, company_name, cursor)
        ic_pe_json = company.to_quarterly_financials_json(db.cursor)
        return json.dumps(ic_pe_json, default = str)

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

    @app.route('/sub_industries/')
    def find_all_sub_industries():
        conn = db.get_db()
        cursor = conn.cursor()
        objs_list = db.find_all(models.SubIndustry, cursor)
        dicts_list = [obj.__dict__ for obj in objs_list]
        return json.dumps(dicts_list)
    
    # 03/03/2021
    @app.route('/sub_industries/<sub_industry_name>')
    def sub_industry_by_name(sub_industry_name):
        """
        Returns a sub_industry's average value of various performance measurements each
        quarter, over four consecutive quarters.
        The measurements include revenue, cost, earnings, stock price, price/earnings ratios.
        """
        conn = db.get_db()
        cursor = conn.cursor()
        
        quarterly_numbers_history = []
        reports_dates_list = db.report_dates(cursor)
        for report_date in reports_dates_list:
            single_quarter_record_obj = db.sub_industry_quarterly_avg_numbers(models.SubIndustryPerformance, 
                                                                            sub_industry_name, 
                                                                            report_date, 
                                                                            cursor)
            quarterly_numbers_history.append(single_quarter_record_obj.__dict__)
        return json.dumps(quarterly_numbers_history)

    @app.route('/sub_industries/search')
    def search_sub_industires():
        conn = db.get_db()
        cursor = conn.cursor()
        params = dict(request.args)
        sub_industry_name = params['sub_industry']
        # generate a list of companies in the same sub_industry
        companies_info = [company.__dict__ for company 
                                    in db.find_companies_by_sub_industry_name(models.Company, sub_industry_name, cursor)]
        """
        # generate of list of quarterly performance numbers, by calling the relevant db method
        quarterly_numbers_history = []
        reports_dates_list = db.report_dates(cursor)
        for report_date in reports_dates_list:
            report_date = datetime.strptime(report_date, '%Y-%m-%d')
            single_quarter_record_obj = db.sub_industry_quarterly_avg_numbers(models.SubIndustryPerformance, 
                                                                            sub_industry_name, 
                                                                            report_date, 
                                                                            cursor)
            quarterly_numbers_history.append(single_quarter_record_obj.__dict__)
        """
        sub_industry_info = {}
        sub_industry_info['companies'] = companies_info
        # sub_industry_info['quarterly numbers'] = quarterly_numbers_history
        return json.dumps(sub_industry_info)



    @app.route('/sectors/sector/<sector_name>')
    def companies_within_sector(sector_name): #may need to work out sub_industries_within_sector
        conn = db.get_db()
        cursor = conn.cursor()
        companies = db.show_companies_by_sector(models.Company, sector_name, cursor)
        for company in companies:
            company.to_quarterly_reports_prices_pe_json_by_ticker(cursor)
        companies_dicts = [company.__dict__ for company in companies]
        return json.dumps(companies_dicts, default = str)

    @app.route('/sectors/sector/search/')
    def companies_by_sector():
        conn = db.get_db()
        cursor = conn.cursor()
        params = dict(request.args)
        sector_name = params['sector']
        breakpoint()
        companies = db.show_companies_by_sector(models.Company, sector_name, cursor)
        for company in companies:
            company.to_quarterly_financials_json(cursor)
        companies_dicts = [company.__dict__ for company in companies]
        return json.dumps(companies_dicts, default = str)
    
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
    """