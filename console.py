import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters

"""
# sub_industries
sub_industries_3 = [{'sub_industry_GICS': 'Hypermarkets & Super Centers', 'sector_GICS': 'Consumer Staples'},
                    {'sub_industry_GICS': 'Pharmaceuticals', 'sector_GICS': 'Health Care'},
                    {'sub_industry_GICS': 'Technology Hardware, Storage & Peripherals', 'sector_GICS': 'Information Technology'}]

sub_industry_builder = adapters.SubIndustryBuilder()
for sub_industry_info in sub_industries_3:
    sub_industry_builder.run(sub_industry_info, db.conn, db.cursor)


# test adapters.CompanyBuilder
# company_info obtained from /Project_development/project_scoping_prototyping/prototyping/company_info_via_intrinio_n_sp500_csv
company_info = {'name': 'APPLE INC',
                'ticker': 'AAPL',
                'number_of_employees': 132000,
                'HQ_state': 'California',
                'country': 'United States of America',
                'year_founded': '1977',
                'sub_industry_name': 'Technology Hardware, Storage & Peripherals'}

builder = adapters.CompanyBuilder()
builder.run(company_info, db.conn, db.cursor)


# 01/03 adapters.QuarterlyReport
# companies_6 = ['WMT', 'COST', 'PFE', 'JNJ', 'AAPL', 'HPQ']
# 2 companies returned from Intrinio
# in notebook "company_quarterly_financials_via_intrinio_api"

wmt_aapl_2020q3 = [{'Total Revenue': 127991000000, 
                    'Total Cost of Revenue': 95900000000, 
                    'Consolidated Net Income / (Loss)': 3321000000, 
                    'Basic Earnings per Share': 1, 
                    'date': "2019-10-31", 
                    'ticker': 'WMT'},
                    {'Total Revenue': 59685000000, 
                    'Total Cost of Revenue': 37005000000, 
                    'Consolidated Net Income / (Loss)': 11253000000, 
                    'Basic Earnings per Share': 2, 
                    'date': "2020-6-27", 
                    'ticker': 'AAPL'}]
wmt_aapl_builder = adapters.QuarterlyReportBuilder()
for q3_financials in wmt_aapl_2020q3:
    wmt_aapl_builder.run(q3_financials, db.conn, db.cursor)


1/1/2021
$python3 -i console.py

>>> import datetime
>>> apple_details = {'Total Revenue': 88293000000,
...  'Total Cost of Revenue': 54381000000,
...  'Consolidated Net Income / (Loss)': 20065000000,
...  'Basic Earnings per Share': 3,
...  'date': datetime.date(2017, 12, 30),
...  'ticker': 'AAPL'}

>>> apple_report = adapters.QuarterlyReport()

>>> apple_report.run(apple_details, db.conn, db.cursor)

"""

# store Apple's most recent 4 quarterly reports that are 
# available from Intrinio API.

apple_3_financials = [{'Total Revenue': 58313000000,
                        'Total Cost of Revenue': 35943000000,
                        'Consolidated Net Income / (Loss)': 11249000000,
                        'Basic Earnings per Share': 2,
                        'date': '2020-03-28',
                        'ticker': 'AAPL'},
                        {'Total Revenue': 91819000000,
                        'Total Cost of Revenue': 56602000000,
                        'Consolidated Net Income / (Loss)': 22236000000,
                        'Basic Earnings per Share': 5,
                        'date': '2019-12-28',
                        'ticker': 'AAPL'},
                        {'Total Revenue': 64040000000,
                        'Total Cost of Revenue': 39727000000,
                        'Consolidated Net Income / (Loss)': 13686000000,
                        'Basic Earnings per Share': 2,
                        'date': '2019-09-28',
                        'ticker': 'AAPL'}]

quarterly_reports_builder = adapters.QuarterlyReportBuilder()
for qtr in apple_3_financials:
    quarterly_reports_builder.run(qtr, db.conn, db.cursor)
