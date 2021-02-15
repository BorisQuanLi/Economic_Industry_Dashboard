import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters

# ETL functions

def extract_companies_info(tickers_list): 
    return (adapters.api_calls.
                        company_info_via_intrinio_n_sp500_csv.
                            companies_info_via_intrinio_api_n_sp500_csv(tickers_list))   

def extract_quarterly_reports(list_of_tickers, end_date = '2021-01-01',
                                number_of_quarters = 4):
    return(adapters.api_calls.quarterly_reports.
                get_companies_multiple_quarters_financials(list_of_tickers,
                                                            end_date = end_date,
                                                            number_of_quarters = number_of_quarters))

# Build functions

def build_companies(companies_info_list, 
                    conn= db.conn, 
                    cursor= db.cursor):
    companies_builder = adapters.CompanyBuilder()
    for company_info in companies_info_list:
        companies_builder.run(company_info, conn, cursor)

def build_quarterly_reports(companies_quarterly_reports_list: list, 
                            conn= db.conn, 
                            cursor= db.cursor):
    quarterly_reports_builder = adapters.QuarterlyReportBuilder()
    for company_quarterly_reports in companies_quarterly_reports_list:
        for quarterly_report in company_quarterly_reports:
            quarterly_reports_builder.run(quarterly_report, conn, cursor)

# PricePE build_extract function 
def build_prices_pe(ticker: str):
    """
    Generate a list of one company's quarterly reports, each a QuarterlyReport object

    Based on the date of each quarterly report, obtains the closing price, then
    calucates the price / earnings ratio, before writing the row of data
    into the prices_pe table. 
    """
    quarterly_reports_objs_list = (models.QuarterlyReport.
                                        find_quarterly_reports_by_ticker(ticker, db.cursor))
    price_pe_builder = adapters.PricePEbuilder()
    price_pe_builder.run(quarterly_reports_objs_list, db.conn, db.cursor)

for ticker in ['PFE', 'JNJ', 'AAPL', 'WMT']:
    build_prices_pe(ticker)


"""
# sub_industries
sub_industries_3 = [{'sub_industry_GICS': 'Hypermarkets & Super Centers', 'sector_GICS': 'Consumer Staples'},
                    {'sub_industry_GICS': 'Pharmaceuticals', 'sector_GICS': 'Health Care'},
                    {'sub_industry_GICS': 'Technology Hardware, Storage & Peripherals', 'sector_GICS': 'Information Technology'}]

sub_industry_builder = adapters.SubIndustryBuilder()
for sub_industry_info in sub_industries_3:
    sub_industry_builder.run(sub_industry_info, db.conn, db.cursor)

---
build_companies

pfe_jnj_info = [{'name': 'PFIZER INC',
  'ticker': 'PFE',
  'number_of_employees': 92400,
  'HQ_state': 'New York',
  'country': 'United States of America',
  'year_founded': '1849',
  'sub_industry_name': 'Pharmaceuticals'},
 {'name': 'JOHNSON & JOHNSON',
  'ticker': 'JNJ',
  'number_of_employees': 135100,
  'HQ_state': 'New Jersey',
  'country': 'United States of America',
  'year_founded': '1886',
  'sub_industry_name': 'Pharmaceuticals'}]

build_companies(pfe_jnj_info)

---

build_quarterly_reports

01/09
four_companies = ['PFE', 'JNJ', 'WMT', 'AAPL']
four_qtrs_reports_202012 = extract_quarterly_reports(four_companies,
                                                end_date = '2020-12-15',
                                                number_of_quarters = 2)
breakpoint()
build_quarterly_reports(four_qtrs_reports_202012)

---
01/03/2020
# build PricePE row in the database based on a company's
# quarterly report (or a history of quarterly reports)

# create a list of all quarterly_reports by a company (ticker)
import api.src.models
apple_qtr_report = api.src.models.QuarterlyReport() 
apple_quarterly_reports = apple_qtr_report.find_quarterly_reports_by_ticker('AAPL', api.src.db.cursor)

# ready to be passed through to adapters.PricePEbuilder
price_pe_builder = adapters.PricePEbuilder()
apple_price_de_dict_list = price_pe_builder.price_pe_dict_list(apple_quarterly_reports, db.cursor)
apple_attributes_list = price_pe_builder.select_attributes(apple_price_de_dict_list)

price_pe_list = []
for apple_attributes in apple_attributes_list:
    price_pe = db.save(models.PricePE(**apple_attributes), db.conn, db.cursor)
    price_pe_list.append(price_pe)
print(price_pe_list)

breakpoint() # inspect apple_price_de_dict_list

# 01/04/2020
# Walmart quarterly_reports obtained in notebook "obtaining Quarterly Reports data, revenue, cost, net income, earnings per share, via Intrinio get_company_historical_data method, 01-04-2020"

# can import the api client in this file:
# import api.src.adapters.api_calls.historical_stock_price_via_intrinio_api
# or the quarterly_report notebook above

01/06/2021
for ticker in ['PFE', 'JNJ', 'AAPL', 'WMT']:
    build_prices_pe(ticker)

"""