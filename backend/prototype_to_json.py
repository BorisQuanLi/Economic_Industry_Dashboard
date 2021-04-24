from api.src.models.company import *
from api.src.db.db import *
import psycopg2
import simplejson as json
from datetime import time, datetime, timedelta
import pandas as pd
import pandas_market_calendars as mcal

conn = psycopg2.connect(database = 'investment_analysis_test', user = 'postgres', password = 'postgres')
cursor = conn.cursor()

# state = find_or_create_by_name(src.State, state_name, conn, cursor)

def find_by_name(Class, col_name, conn, cursor):
    sql_str = f"""SELECT * FROM {Class.__table__}
                    WHERE col_name = %s;
                    """
    cursor.execute(sql_str)
    records = cursor.fetchall()
    return build_from_records(Class, records)

# revenue_energy_sub_industries = find_sub_industries_by_sector('Energy', 'revenue').json()
a_dict = {'Oil & Gas Exploration & Production': {'id': 159, 'sub_industry_GICS': 'Oil & Gas Exploration & Production', 'sector_GICS': 'Energy', 'Avg_quarterly_profit_margins': {'2019-02': 14, '2019-03': -13, '2019-04': -29, '2020-01': -57, '2020-02': -164, '2020-03': -30, '2020-04': -14}}, 'Oil & Gas Storage & Transportation': {'id': 230, 'sub_industry_GICS': 'Oil & Gas Storage & Transportation', 'sector_GICS': 'Energy', 'Avg_quarterly_profit_margins': {'2019-03': 15, '2019-04': 12, '2020-01': -14, '2020-02': 0, '2020-03': 15, '2020-04': 8}}, 'Oil & Gas Equipment & Services': {'id': 171, 'sub_industry_GICS': 'Oil & Gas Equipment & Services', 'sector_GICS': 'Energy', 'Avg_quarterly_profit_margins': {'2019-04': -10, '2020-01': -104, '2020-02': -31, '2020-03': -2, '2020-04': -3}}, 'Integrated Oil & Gas': {'id': 191, 'sub_industry_GICS': 'Integrated Oil & Gas', 'sector_GICS': 'Energy', 'Avg_quarterly_profit_margins': {'2019-04': -7, '2020-01': -56, '2020-02': -31, '2020-03': -7, '2020-04': -17}}, 'Oil & Gas Refining & Marketing': {'id': 223, 'sub_industry_GICS': 'Oil & Gas Refining & Marketing', 'sector_GICS': 'Energy', 'Avg_quarterly_profit_margins': {'2019-04': 2, '2020-01': -18, '2020-02': 3, '2020-03': -4, '2020-04': 0}}}

for sub_industry, attr_dicts in a_dict.items():
    dates_list = list(attr_dicts['Avg_quarterly_profit_margins'].keys())
    values_list = list(attr_dicts['Avg_quarterly_profit_margins'].values())
    name = sub_industry
    breakpoint()

breakpoint()

apa_dict = dict(zip(['id', 'name', 'ticker', 'sub_industry_id', 'year_founded','number_of_employees', 'HQ_state'],
                 [45, 'APA Corporation', 'APA', '159', '1954', '3163', 'Texas']))

apa_obj = Company(**apa_dict)
quarterly_reports_prices_pe_json = apa_obj.to_quarterly_financials_json(cursor)

####
# debug simplejson.dump 

import simplejson as json

historical_financials_json_dicts = [{'id': 159, 'sub_industry_GICS': 'Oil & Gas Exploration & Production', 'sector_GICS': 'Energy', ('revenue', 'Oil & Gas Exploration & Production', 'Energy'): [4420000000, 5687000000, 2349763750, 2204362500, 959420750, 1158739857, 1349488429]}, {'id': 230, 'sub_industry_GICS': 'Oil & Gas Storage & Transportation', 'sector_GICS': 'Energy', ('revenue', 'Oil & Gas Storage & Transportation', 'Energy'): [3214000000, 2707535333, 2385224000, 2000576333, 2342088000, 2331288500]}, {'id': 171, 'sub_industry_GICS': 'Oil & Gas Equipment & Services', 'sector_GICS': 'Energy', ('revenue', 'Oil & Gas Equipment & Services', 'Energy'): [5512000000, 4950000000, 3696000000, 3666500000, 3897750000]}, {'id': 191, 'sub_industry_GICS': 'Integrated Oil & Gas', 'sector_GICS': 'Energy', ('revenue', 'Integrated Oil & Gas', 'Energy'): [33093666667, 28731000000, 16345333333, 23527000000, 23967333333]}, {'id': 223, 'sub_industry_GICS': 'Oil & Gas Refining & Marketing', 'sector_GICS': 'Energy', ('revenue', 'Oil & Gas Refining & Marketing', 'Energy'): [29365333333, 22731666667, 12111333333, 16382000000, 17241666667]}]
a_dict = historical_financials_json_dicts
breakpoint()
json.dumps(historical_financials_json_dicts, default = str)

"""
-> return json.dumps(historical_financials_json_dicts, default = str)
(Pdb) json.dumps(historical_financials_json_dicts, default = str)

*** TypeError: keys must be str, int, float, bool or None, not tuple
"""
breakpoint()

"""
-> quarterly_reports_prices_pe_json['Quarterly_financials'] = [
(Pdb) quarterly_reports_obj
[<api.src.models.quarterly_report.QuarterlyReport object at 0x7f8d46068820>, <api.src.models.quarterly_report.QuarterlyReport object at 0x7f8d463c5a90>, <api.src.models.quarterly_report.QuarterlyReport object at 0x7f8d463c59a0>, <api.src.models.quarterly_report.QuarterlyReport object at 0x7f8d463cdb20>, <api.src.models.quarterly_report.QuarterlyReport object at 0x7f8d4639f3d0>]

(Pdb) quarterly_reports_obj[0].__dict__
{'id': 112, 'date': '2020-12-31', 'company_id': 45, 'revenue': 1219000000, 'net_income': 30000000, 'earnings_per_share': 0.03, 'profit_margin': 2.46}
"""

"""select sub_industries.id, sub_industries.sub_industry_gics, 
                            ROUND(AVG(quarterly_reports.revenue), 0), 
                            EXTRACT(year from quarterly_reports.date::DATE) as year, 
                            EXTRACT(quarter from quarterly_reports.date::DATE) as quarter
                        FROM sub_industries 
                        JOIN companies ON sub_industries.id = companies.sub_industry_id::INTEGER
                        JOIN quarterly_reports ON quarterly_reports.company_id::INTEGER = companies.id
                        WHERE sub_industries.sector_gics = 'Energy'
                        GROUP BY year, quarter, sub_industries.id, sub_industries.sub_industry_gics
                        LIMIT 15;
                    """

"""select sub_industries.id, sub_industries.sub_industry_gics, 
                            ROUND(AVG(quarterly_reports.revenue), 0), 
                            EXTRACT(year from quarterly_reports.date::DATE) as year, 
                            EXTRACT(quarter from quarterly_reports.date::DATE) as quarter
                        FROM sub_industries 
                        JOIN companies ON sub_industries.id = companies.sub_industry_id::INTEGER
                        JOIN quarterly_reports ON quarterly_reports.company_id::INTEGER = companies.id
                        WHERE sub_industries.sector_gics = 'Energy'
                        AND sub_industries.sub_industry_gics = 'Oil & Gas Exploration & Production';
                    """

"""
select sub_industries.id, sub_industries.sub_industry_gics,
                            ROUND(AVG(profit_margin)::NUMERIC, 2) as profit_margin,
                            EXTRACT(year from quarterly_reports.date::DATE) as year,
                            EXTRACT(quarter from quarterly_reports.date::DATE) as quarter
                        FROM quarterly_reports
                        JOIN companies ON quarterly_reports.company_id::INTEGER = companies.id
                        JOIN sub_industries ON sub_industries.id = companies.sub_industry_id::INTEGER
                        WHERE sub_industries.sector_gics = 'Energy'
                        GROUP BY year, quarter, sub_industries.id, sub_industries.sub_industry_gics;
"""