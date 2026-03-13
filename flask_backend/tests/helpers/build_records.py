from api.src.db.db import save
from api.src.models.sub_industry import SubIndustry
from api.src.models.company import Company
from api.src.models.quarterly_report import QuarterlyReport
from api.src.models.price_pe import PricePE

def build_records(test_conn, test_cursor):
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
    semiconductor_company1 = save(Company(**dict(zip(['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state'],
                                                ['semiconductor_company1', 'semi_cond_1', str(semiconductor_info_tech.id), '2001', '2001', 'BB']))), test_conn, test_cursor)
    life_ins_company1 = save(Company(**dict(zip(['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state'],
                                                ['life_ins_company1', 'life_ins_1', str(life_insurance_fin.id), '2002', '2002', 'CC']))), test_conn, test_cursor)
    inv_bank_company1 = save(Company(**dict(zip(['name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state'],
                                                ['inv_bank_company1', 'inv_bank_1', str(invest_banking_fin.id), '2003', '2003', 'DD']))), test_conn, test_cursor)
    
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
                                                                            ['2020-12-31', semiconductor_company1.id, 100, 1.1]))), test_conn, test_cursor)
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
