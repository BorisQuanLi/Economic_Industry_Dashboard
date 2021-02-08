import pytest
from api.src.db.db import save, drop_all_tables, get_db, find_all, find, close_db 
from api.src.models import Company, SubIndustry, QuarterlyReport, PricePE, SubIndustryPerformance
from api.src import create_app

def build_records(test_conn, test_cursor):
    merck_dict = {'name': 'Merck & Co., Inc.', 'ticker': 'MRK', 'number_of_employees': 69000, 
                    'HQ_state': 'New Jersey', 'country': 'United States of America', 
                    'year_founded': '1891', 'sub_industry_name': 'Pharmaceuticals'}
    merck_obj = Company(**merck_dict)
    merck = save(merck_obj, test_conn, test_cursor)

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
    
def test_company_sector(company_obj, cursor):
    sub_industry_obj = company_obj.sub_industry(cursor)
    sector_name = sub_industry_obj.__dict__['sector_GICS']
    assert sector_name == "Health Care"
    
