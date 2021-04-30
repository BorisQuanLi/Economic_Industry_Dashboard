import pytest
from api.src.models import Company, SubIndustry, QuarterlyReport, PricePE
from api.src.db.db import save, drop_all_tables, get_db, find_all, find, close_db
from api.src import create_app

# hard-code the revenue number of a particular quarter, 2-3 companies' number
def build_records(test_conn, test_cursor): # move this to a fixture.py in the test folder.
    # create Sectors and Sub_industries
    app_sw_info_tech = save(SubIndustry(**dict(zip(['sub_industry_GICS', 'sector_GICS'],
                                            ['Application Software', 'Information Technology']))), test_conn, test_cursor)
    semiconductor_info_tech = save(SubIndustry(**dict(zip(['sub_industry_GICS', 'sector_GICS'],
                                            ['Semiconductors', 'Information Technology']))), test_conn, test_cursor)
    life_insurance_fin = save(SubIndustry(**dict(zip(['sub_industry_GICS', 'sector_GICS'],
                                            ['Life & Health Insurance', 'Financials']))), test_conn, test_cursor)
    invest_banking_fin = save(SubIndustry(**dict(zip(['sub_industry_GICS', 'sector_GICS'],
                                            ['Investment Banking & Brokerage', 'Financials']))), test_conn, test_cursor)

    # create companies within each sub-industries
    app_sw_company1 = save(Company(**dict(zip(['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state'],
                                                ['app_sw_company1', 'app_sw_1', str(app_sw_info_tech.id), '2000', '2000', 'AA']))), test_conn, test_cursor)
    app_sw_company2 = save(Company(**dict(zip(['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state'],
                                                ['app_sw_company2', 'app_sw_2', str(app_sw_info_tech.id), '1990', '1990', 'ZZ']))), test_conn, test_cursor)
    semiconductor_company1 = save(Company(**dict(zip(['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state'],
                                                ['semiconductor_company1', 'semi_cond_1', str(semiconductor_info_tech.id), '2001', '2001', 'BB']))), test_conn, test_cursor)
    semiconductor_company2 = save(Company(**dict(zip(['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state'],
                                                ['semiconductor_company2', 'semi_cond_2', str(semiconductor_info_tech.id), '1991', '1991', 'YY']))), test_conn, test_cursor)                                            
    life_ins_company1 = save(Company(**dict(zip(['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state'],
                                                ['life_ins_company1', 'life_ins_1', str(life_insurance_fin.id), '2002', '2002', 'CC']))), test_conn, test_cursor)
    life_ins_company2 = save(Company(**dict(zip(['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state'],
                                                ['life_ins_company2', 'life_ins_2', str(life_insurance_fin.id), '1992', '1992', 'XX']))), test_conn, test_cursor)
    inv_bank_company1 = save(Company(**dict(zip(['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state'],
                                                ['inv_bank_company1', 'inv_bank_1', str(invest_banking_fin.id), '2003', '2003', 'DD']))), test_conn, test_cursor)
    inv_bank_company2 = save(Company(**dict(zip(['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state'],
                                                ['inv_bank_company2', 'inv_bank_2', str(invest_banking_fin.id), '1993', '1993', 'WW']))), test_conn, test_cursor)

    # create quarterly_reports for each company, semiconductor_company1
    semiconductor_company1_qtr5 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-12-31', semiconductor_company1.id, 2000, 100, 1.1, 0.05]))), test_conn, test_cursor)
    semiconductor_company1_qtr4 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-09-30', semiconductor_company1.id, 1800, 90, 1.0, 0.05]))), test_conn, test_cursor)
    semiconductor_company1_qtr3 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-06-30', semiconductor_company1.id, 1600, 80, 0.9, 0.05]))), test_conn, test_cursor)
    semiconductor_company1_qtr2 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-03-30', semiconductor_company1.id, 1400, 70, 0.8, 0.05]))), test_conn, test_cursor)
    semiconductor_company1_qtr1 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2019-12-30', semiconductor_company1.id, 2200, 110, 1.2, 0.05]))), test_conn, test_cursor)
    
    semiconductor_company2_qtr5 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-12-31', semiconductor_company2.id, 3000, 600, 1.1, 0.20]))), test_conn, test_cursor)
    semiconductor_company2_qtr4 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-09-30', semiconductor_company2.id, 2800, 540, 1.0, 0.20]))), test_conn, test_cursor)
    semiconductor_company2_qtr3 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-06-30', semiconductor_company2.id, 2600, 520, 0.9, 0.20]))), test_conn, test_cursor)
    semiconductor_company2_qtr2 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-03-30', semiconductor_company2.id, 2400, 480, 0.8, 0.20]))), test_conn, test_cursor)
    semiconductor_company2_qtr1 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2019-12-30', semiconductor_company2.id, 3200, 640, 1.2, 0.20]))), test_conn, test_cursor)
    
    # create quarterly_reports for each company, app_sw_company1
    app_sw_company1_qtr5 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-12-31', app_sw_company1.id, 1000, 100, 1.1, 0.1]))), test_conn, test_cursor)
    app_sw_company1_qtr4 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-09-30', app_sw_company1.id, 900, 90, 1.0, 0.1]))), test_conn, test_cursor)
    app_sw_company1_qtr3 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-06-30', app_sw_company1.id, 800, 80, 0.9, 0.1]))), test_conn, test_cursor)
    app_sw_company1_qtr2 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-03-30', app_sw_company1.id, 700, 70, 0.8, 0.1]))), test_conn, test_cursor)
    app_sw_company1_qtr1 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2019-12-30', app_sw_company1.id, 1100, 110, 1.2, 0.1]))), test_conn, test_cursor)
    
    app_sw_company2_qtr5 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-12-31', app_sw_company2.id, 1500, 150, 1.1, 0.1]))), test_conn, test_cursor)
    app_sw_company2_qtr4 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-09-30', app_sw_company2.id, 1350, 135, 1.0, 0.1]))), test_conn, test_cursor)
    app_sw_company2_qtr3 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-06-30', app_sw_company2.id, 1200, 120, 0.9, 0.1]))), test_conn, test_cursor)
    app_sw_company2_qtr2 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-03-30', app_sw_company2.id, 1050, 105, 0.8, 0.1]))), test_conn, test_cursor)
    app_sw_company2_qtr1 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2019-12-30', app_sw_company2.id, 1650, 165, 1.2, 0.1]))), test_conn, test_cursor)

    # create quarterly_reports for each company, life_insurance_company1
    life_insurance_company1_qtr5 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-12-31', life_ins_company1.id, 20000, 1000, 1.1, 0.05]))), test_conn, test_cursor)
    life_insurance_company1_qtr4 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-09-30', life_ins_company1.id, 18000, 900, 1.0, 0.05]))), test_conn, test_cursor)
    life_insurance_company1_qtr3 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-06-30', life_ins_company1.id, 16000, 800, 0.9, 0.05]))), test_conn, test_cursor)
    life_insurance_company1_qtr2 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-03-30', life_ins_company1.id, 14000, 700, 0.8, 0.05]))), test_conn, test_cursor)
    life_insurance_company1_qtr1 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2019-12-30', life_ins_company1.id, 22000, 1100, 1.2, 0.05]))), test_conn, test_cursor)
    
    # create quarterly_reports for each company, inv_bank_company1
    inv_bank_company1_qtr5 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-12-31', inv_bank_company1.id, 10000, 1000, 1.1, 0.1]))), test_conn, test_cursor)
    inv_bank_company1_qtr4 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-09-30', inv_bank_company1.id, 9000, 900, 1.0, 0.1]))), test_conn, test_cursor)
    inv_bank_company1_qtr3 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-06-30', inv_bank_company1.id, 8000, 800, 0.9, 0.1]))), test_conn, test_cursor)
    inv_bank_company1_qtr2 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2020-03-30', inv_bank_company1.id, 7000, 700, 0.8, 0.1]))), test_conn, test_cursor)
    inv_bank_company1_qtr1 = save(QuarterlyReport(**dict(zip(['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'],
                                                ['2019-12-30', inv_bank_company1.id, 11000, 1100, 1.2, 0.1]))), test_conn, test_cursor)
    
    # create prices_pe record for each company, semiconductor_company1
    semiconductor_company1_price_pe_qtr5 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-12-31', semiconductor_company1.id, 100.0, 1.1]))), test_conn, test_cursor)
    semiconductor_company1_price_pe_qtr4 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-09-30', semiconductor_company1.id, 90, 1.0]))), test_conn, test_cursor)
    semiconductor_company1_price_pe_qtr3 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-06-30', semiconductor_company1.id, 80, 0.9]))), test_conn, test_cursor)
    semiconductor_company1_price_pe_qtr2 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-03-30', semiconductor_company1.id, 70, 0.8]))), test_conn, test_cursor)
    semiconductor_company1_price_pe_qtr1 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2019-12-30', semiconductor_company1.id, 110, 1.2]))), test_conn, test_cursor)
    
    # create prices_pe for each company, app_sw_company1
    app_sw_company1_price_pe_qtr5 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-12-31', app_sw_company1.id, 110, 1.1]))), test_conn, test_cursor)
    app_sw_company1_price_pe_qtr4 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-09-30', app_sw_company1.id, 100, 1.0]))), test_conn, test_cursor)
    app_sw_company1_price_pe_qtr3 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-06-30', app_sw_company1.id, 90, 0.9]))), test_conn, test_cursor)
    app_sw_company1_price_pe_qtr2 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-03-30', app_sw_company1.id, 80, 0.8]))), test_conn, test_cursor)
    app_sw_company1_price_pe_qtr1 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2019-12-30', app_sw_company1.id, 120, 1.2]))), test_conn, test_cursor)
    
    # create prices_pe for each company, life_insurance_company1
    life_insurance_company1_price_pe_qtr5 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-12-31', life_ins_company1.id, 1000, 1.1]))), test_conn, test_cursor)
    life_insurance_company1_price_pe_qtr4 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-09-30', life_ins_company1.id, 900, 1.0]))), test_conn, test_cursor)
    life_insurance_company1_price_pe_qtr3 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-06-30', life_ins_company1.id, 800, 0.9]))), test_conn, test_cursor)
    life_insurance_company1_price_pe_qtr2 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-03-30', life_ins_company1.id, 700, 0.8]))), test_conn, test_cursor)
    life_insurance_company1_price_pe_qtr1 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2019-12-30', life_ins_company1.id, 1100, 1.2]))), test_conn, test_cursor)
    
    # create prices_pe for each company, inv_bank_company1
    inv_bank_company1_price_pe_qtr5 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-12-31', inv_bank_company1.id, 1000, 1.1]))), test_conn, test_cursor)
    inv_bank_company1_price_pe_qtr4 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-09-30', inv_bank_company1.id, 900, 1.0]))), test_conn, test_cursor)
    inv_bank_company1_price_pe_qtr3 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-06-30', inv_bank_company1.id, 800, 0.9]))), test_conn, test_cursor)
    inv_bank_company1_price_pe_qtr2 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2020-03-30', inv_bank_company1.id, 700, 0.8]))), test_conn, test_cursor)
    inv_bank_company1_price_pe_qtr1 = save(PricePE(**dict(zip(['date', 'company_id', 'closing_price', 'price_earnings_ratio'],
                                                ['2019-12-30', inv_bank_company1.id, 1100, 1.2]))), test_conn, test_cursor)
    

@pytest.fixture()
def db_cursor():
    flask_app = create_app(database='investment_analysis_test', testing = True, debug = True)

    with flask_app.app_context(): # flask method app_context.  No need to involve .env
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
    assert avg_qtr_rev_by_Energy_sub_industries['Semiconductors'][
                                            'Avg_quarterly_revenues']['2020-04'] == 2500

def test_avg_revenue_application_sw_2020_4th_qtr(db_cursor):
    sector_name = 'Information Technology'
    fin_statement_item = 'revenue'
    avg_qtr_rev_by_Energy_sub_industries = SubIndustry.find_avg_quarterly_financials_by_sub_industry(
                                                                                    sector_name, fin_statement_item, db_cursor)
    assert avg_qtr_rev_by_Energy_sub_industries['Application Software'][
                                            'Avg_quarterly_revenues']['2020-04'] == 1250
