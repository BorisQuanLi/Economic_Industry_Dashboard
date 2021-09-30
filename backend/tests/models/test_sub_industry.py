import pytest
from api.src.models import Company, SubIndustry, QuarterlyReport, PricePE
from api.src.db.db import save, drop_all_tables, get_db, find_all, find, close_db
from api.src import create_app
from tests.models.test_app import build_records

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

def test_value_most_recent_quater(db_cursor):
    sector_name = 'Information Technology'
    fin_statement_item = 'revenue'
    avg_sub_industry_qtr_revs_in_info_tech = SubIndustry.find_avg_quarterly_financials_by_sub_industry(
                                                                                    sector_name, fin_statement_item, db_cursor)
    value_most_recent_quarter = (int(avg_sub_industry_qtr_revs_in_info_tech['Semiconductors'][-1]['year']) * 100
                            + int(avg_sub_industry_qtr_revs_in_info_tech['Semiconductors'][-1]['quarter']))
    assert value_most_recent_quarter == 202004

def test_semiconductors_avg_revenue_2020_4th_qtr(db_cursor):
    sector_name = 'Information Technology'
    fin_statement_item = 'revenue'
    avg_sub_industry_qtr_revs_in_info_tech = SubIndustry.find_avg_quarterly_financials_by_sub_industry(
                                                                                    sector_name, fin_statement_item, db_cursor)
    most_recent_qtr_semiconductors_sub_industry_avg_rev = int(avg_sub_industry_qtr_revs_in_info_tech['Semiconductors'][-1]['revenue'])
    assert most_recent_qtr_semiconductors_sub_industry_avg_rev == 2000

def test_app_sw_avg_revenue_2020_4th_qtr(db_cursor):
    sector_name = 'Information Technology'
    fin_statement_item = 'revenue'
    avg_sub_industry_qtr_revs_in_info_tech = SubIndustry.find_avg_quarterly_financials_by_sub_industry(
                                                                                    sector_name, fin_statement_item, db_cursor)
    most_recent_qtr_app_sw_sub_industry_avg_rev = int(avg_sub_industry_qtr_revs_in_info_tech['Application Software'][-1]['revenue'])
    assert most_recent_qtr_app_sw_sub_industry_avg_rev == 1000
