import pytest
from api.src.db.db import save, drop_all_tables, get_db, find_all, find, close_db 
from api.src.models import Company, SubIndustry, QuarterlyReport, PricePE, SubIndustryPerformance
from api.src import create_app

"""
02/10/2021. Execution context:
project_folder borisli$ python3 -m pytest tests/
"""

def build_records(test_conn, test_cursor):
    airlines_sub_industry_dict = {'sub_industry_GICS': 'Airlines', 'sector_GICS': 'Industrials'}
    airlines_sub_industry_obj = save(SubIndustry(**airlines_sub_industry_dict), 
                                                                    test_conn, test_cursor)
    airlines_sub_industry_id = airlines_sub_industry_obj.id

    united_airlines_dict = {'name': 'United Airlines Holdings', 'ticker': 'UAL', 'year_founded': '1967'}
    united_airlines_dict['sub_industry_id'] = airlines_sub_industry_id
    united_airlines_company_obj = save(Company(**united_airlines_dict), 
                                                                test_conn, test_cursor)

@pytest.fixture()
def db_cursor():
    flask_app = create_app()

    with flask_app.app_context():
       conn = get_db()
       cursor = conn.cursor()
    drop_all_tables(conn, cursor)
    build_records(conn, cursor)
    
    yield cursor
    
    with flask_app.app_context():
        close_db()
        conn = get_db()
        cursor = conn.cursor()
        drop_all_tables(conn, cursor)
        close_db()

# test a Class method
def test_find_by_ticker(db_cursor):
    united_airlines_name = Company.find_by_stock_ticker("UAL" , db_cursor).name
    assert united_airlines_name == 'United Airlines Holdings'

# test an instance method
def test_sub_industry(db_cursor):
    """
    returns a company's sub_industry
    """
    united_airlines = Company.find_by_stock_ticker("UAL", db_cursor)
    sub_industry = united_airlines.sub_industry(db_cursor)
    assert sub_industry.sector_GICS == 'Industrials'
    
# test to_json method