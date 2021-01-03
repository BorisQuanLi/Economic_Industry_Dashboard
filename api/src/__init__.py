# Ref. foursquare_development rep, src/__init__.py

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
        return 'Welcome to the stocks performance api, through the prism of the S&P 500.'

    @app.route('/companies')
    def companies():
        conn = db.get_db()
        cursor = conn.cursor()

        companies = db.find_all(models.Company, cursor)
        company_dicts = [company.__dict__ for company in companies]
        return json.dumps(company_dicts, default = str)

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

    @app.route('/companies/<id>')
    def company(id):
        conn = db.get_db()
        cursor = conn.cursor()
        company = db.find(models.Company, id, cursor)
        return json.dumps(company.__dict__, default = str)

    @app.route('/companies/tickers/<ticker>') 
    def ticker(ticker):
        conn = db.get_db()
        cursor = conn.cursor()
        company = db.find_by_ticker(models.Company, ticker, cursor)
        quarterly_reports = company.quarterly_reports(cursor) #company.quarterly_reports
        company_dict = company.__dict__
        quarterly_reports_dicts = [quarterly_report.__dict__ for quarterly_report in quarterly_reports]
        company_dict['quarterly_reports'] = quarterly_reports_dicts
        return json.dumps(company.__dict__, default = str)

    @app.route('/companies/tickers/search')
    def ticker_search():
        conn = db.get_db()
        cursor = conn.cursor()
        params = dict(request.args)
        ticker = params['ticker']
        # return ticker(ticker), can this be implemented?
        company = db.find_by_ticker(models.Company, ticker, cursor)
        quarterly_reports = company.quarterly_reports(cursor) #company.quarterly_reports
        company_dict = company.__dict__
        quarterly_reports_dicts = [quarterly_report.__dict__ for quarterly_report in quarterly_reports]
        company_dict['quarterly_reports'] = quarterly_reports_dicts
        return json.dumps(company.__dict__, default = str)
        



    @app.route('/companies/latest_quarterly_result_company/<ticker>')
    def latest_quarterly_result_company(ticker):
        conn = db.get_db()
        cursor = conn.cursor()
        company_financials = db.find_company_financials_by_ticker(
            models.QuarterlyReport, ticker, cursor)
        return json.dumps(company_financials.__dict__, default = str)

    @app.route('/companies/price_pe/<ticker>')
    def price_pe_company(ticker):
        conn = db.get_db()
        cursor = conn.cursor()
        company_price_pe = db.find_latest_company_price_pe_by_ticker(
            models.PricePE, ticker, cursor)
        company_price_pe = company_price_pe.to_latest_pe_json(cursor)
        return json.dumps(company_price_pe, default = str)

    return app
