import pytest
from api.src.models import Company, SubIndustry, QuarterlyReport, PricePE
from api.src.db.db import save, drop_all_tables, get_db, find_all, find, close_db
from api.src import create_app
from fixture import build_records

@pytest.fixture()
def db_cursor():
    flask_app = create_app(database='investment_analysis_test', testing = True, debug = True)

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

def test_avg_revenue_semiconductor_2020_4th_qtr(db_cursor):
    sector_name = 'Information Technology'
    fin_statement_item = 'revenue'
    avg_qtr_rev_by_Energy_sub_industries = SubIndustry.find_avg_quarterly_financials_by_sub_industry(
                                                                                    sector_name, fin_statement_item, db_cursor)
    assert avg_qtr_rev_by_Energy_sub_industries['Semiconductors'][
                                            'Avg_quarterly_revenues']['2020-04'] == 2500

def test_avg_revenue_semiconductor_2020_4th_qtr(db_cursor):
    sector_name = 'Information Technology'
    fin_statement_item = 'revenue'
    avg_qtr_rev_by_Energy_sub_industries = SubIndustry.find_avg_quarterly_financials_by_sub_industry(
                                                                                    sector_name, fin_statement_item, db_cursor)
    assert avg_qtr_rev_by_Energy_sub_industries['Semiconductors'][0][
                                            'Avg_quarterly_revenue'][202004] == 2500

def test_avg_revenue_application_sw_2020_4th_qtr(db_cursor):
    sector_name = 'Information Technology'
    fin_statement_item = 'revenue'
    avg_qtr_rev_by_Energy_sub_industries = SubIndustry.find_avg_quarterly_financials_by_sub_industry(
                                                                                    sector_name, fin_statement_item, db_cursor)
    assert avg_qtr_rev_by_Energy_sub_industries['Application Software'][0][
                                            'Avg_quarterly_revenue'][202004] == 1250
