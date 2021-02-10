import pytest
from api.src.db.db import save, drop_all_tables, get_db, find_all, find, close_db 
from api.src.models import Company, SubIndustry, QuarterlyReport, PricePE, SubIndustryPerformance
from api.src import create_app

"""
02/10/2021. Execution context:
project_folder borisli$ python3 -m pytest tests/
"""

def build_records(test_conn, test_cursor):
    merck_dict = {'name': 'Merck & Co., Inc.', 'ticker': 'MRK', 'number_of_employees': 69000, 
                    'HQ_state': 'New Jersey', 'country': 'United States of America', 
                    'year_founded': '1891', 'sub_industry_name': 'Pharmaceuticals'}
    merck_obj = Company(**merck_dict)
    # merck = save(merck_obj, test_conn, test_cursor)

    # Notes from discussion with Jeff during the Office Hour
    # make sure the sub_industries table row is created for "Pharmaceuticals" sub_industry and "Health Care" sector
    # In my current case, it is done with Pfizer and Johnson & Johnson,
    # Maybe it should be done with a brand new sub_industry, other than the 3 that have been created in the database

    airlines_dict = {'sub_industry_GICS': 'Airlines', 'sector_GICS': 'Industrials'}
    airlines_sub_industry_obj = save(SubIndustry(**airlines_dict), test_conn, test_cursor)
    airlines_sub_industry_id = airlines_sub_industry_obj.id

    united_airlines_dict = {'': '457', 'Symbol': 'UAL', 'Security': 'United Airlines Holdings', 
                            'SEC filings': 'reports', 'GICS Sector': 'Industrials', 
                            'GICS Sub-Industry': 'Airlines', 'Headquarters Location': 'Chicago, Illinois', 
                            'Date first added': '2015-09-03', 'CIK': '100517', 'Founded': '1967'}
    united_airlines_dict['sub_industry_id'] = airlines_sub_industry_id
    sp500_row_fields_company_columns_dict = {'Security': 'name',
                                            'Symbol': 'ticker',
                                            'sub_industry_id': 'sub_industry_id',
                                            'Founded': 'year_founded'}
    united_airlines_dict= {sp500_row_fields_company_columns_dict[key]:value 
                                for key,value in united_airlines_dict.items() 
                                    if key in sp500_row_fields_company_columns_dict}
    united_airlines_company_obj = Company(**united_airlines_dict)
    united_airlines_company_obj = save(united_airlines_company_obj, test_conn, test_cursor)

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

def test_find_by_ticker(db_cursor):
    united_airlines_ticker = "UAL" 
    united_airlines_name = Company.find_by_stock_ticker(
                                                    united_airlines_ticker, db_cursor).name
    assert united_airlines_name == 'United Airlines Holdings'

def test_company_sector(db_cursor):
    united_airlines_ticker = "UAL" 
    company_obj_united_airlines = Company.find_by_stock_ticker(
                                                            united_airlines_ticker, db_cursor)
    sub_industry_obj = company_obj_united_airlines.sub_industry(db_cursor)
    sector_name = sub_industry_obj.__dict__['sector_GICS']
    assert sector_name == 'Industrials'
    
