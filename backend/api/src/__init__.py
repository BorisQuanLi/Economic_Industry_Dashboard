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

def create_app(db_name='investment_analysis', db_user='postgres', db_password='postgres', testing=False):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)
    
    # connect to the local computer's Postgres
    app.config.from_mapping(
        DB_USER = db_user,
        DB_NAME = db_name,
        DB_PASSWORD = db_password,
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
        return {'message': 'API is running.'}

    from .routes.sector_routes import sector_bp
    from .routes.sub_sector_routes import sub_sector_bp
    from .routes.company_routes import company_bp
    app.register_blueprint(sector_bp)
    app.register_blueprint(sub_sector_bp)
    app.register_blueprint(company_bp)

    return app
