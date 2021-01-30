from flask import Flask
import simplejson as json
from flask import request

import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters

def create_app(database='investment_analysis', testing = False, debug = True):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=database,
        DEBUG = debug,
        TESTING = testing
    )

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
    def find_company_by_name_or_ticker():
        conn = db.get_db()
        cursor = conn.cursor()
        params = dict(request.args)
        for key in params.keys():
            if key == 'ticker':
                ticker = params['ticker']
                company = db.find_by_ticker(models.Company, ticker, cursor)
            else:
                name = params['name']
                company = db.find_by_name(models.Company, name, cursor)
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
    
    @app.route('/sub_industries/<id>')
    def sub_industry(id):
        """
        Return a json list of a sub_industry's average financial in revenues, earnings, p/e ratios.
        """
        conn = db.get_db()
        cursor = conn.cursor()
        sub_industry_obj = db.find(models.SubIndustry, id, cursor)
        #sub_industry_id = sub_industry_obj.id
        sub_industry_obj.average_financials_by_sub_industry(cursor)
        
        breakpoint()
        # a list of Company objects in the same sector
        companies_by_sub_industry = (db.find_companies_by_sub_industry(
                                                                    models.Company, sub_industry_id, cursor))
        print(companies_by_sub_industry)
        breakpoint()
        models.Company.group_avg_financials_history(companies_by_sub_industry, cursor)
        return json.dumps(sub_industry_obj.__dict__)

    @app.route('/sub_industries/search')
    def search_sub_industires():
        sub_industries_name = dict(request.args)['sub_industry']
        
        return sub_industry(id)



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