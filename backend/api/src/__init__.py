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

    from .routes.sector_routes import sector_bp
    app.register_blueprint(sector_bp)

    return app
