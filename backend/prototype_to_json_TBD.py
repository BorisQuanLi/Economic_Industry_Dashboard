from api.src.models.company import *
from api.src.db.db import *
import psycopg2
import simplejson as json
from datetime import time, datetime, timedelta
import pandas as pd
import pandas_market_calendars as mcal
from decimal import *

conn = psycopg2.connect(database = 'investment_analysis_test', user = 'postgres', password = 'postgres')
cursor = conn.cursor()

# 05/05 Reuven Lerner while loop for input

name = True
while name:
    name = input("What's your first name, please? ")
    if name:
        print(f"Your name is all lowercase is spelled: {name.lower()}")
    else: break

breakpoint()
# 05/02 work out plotly chart of financials_by_sector json return
json_return = {'Consumer Staples': {'202001': {'avg_revenue': 12615849903.23, 'avg_net_income': 780862806.45, 'avg_earnings_per_share': 0.99, 'avg_profit_margin': 12.73}, '202002': {'avg_revenue': 12595588838.71, 'avg_net_income': 569776967.74, 'avg_earnings_per_share': 0.69, 'avg_profit_margin': 8.52}, '202003': {'avg_revenue': 13884618172.41, 'avg_net_income': 975771379.31, 'avg_earnings_per_share': 1.35, 'avg_profit_margin': 12.56}, '202004': {'avg_revenue': 13227184107.14, 'avg_net_income': 992984642.86, 'avg_earnings_per_share': 1.37, 'avg_profit_margin': 14.8}, '202101': {'avg_revenue': 22234742076.92, 'avg_net_income': 613684230.77, 'avg_earnings_per_share': 1.96, 'avg_profit_margin': 10.39}}, 'Energy': {'202001': {'avg_revenue': 10069083000.0, 'avg_net_income': -1516083350.0, 'avg_earnings_per_share': -2.71, 'avg_profit_margin': -33.63}, '202002': {'avg_revenue': 5641133850.0, 'avg_net_income': -1358037000.0, 'avg_earnings_per_share': -1.97, 'avg_profit_margin': -74.09}, '202003': {'avg_revenue': 7909252736.84, 'avg_net_income': -231239578.95, 'avg_earnings_per_share': -0.68, 'avg_profit_margin': -11.32}, '202004': {'avg_revenue': 8597901000.0, 'avg_net_income': -1214363888.89, 'avg_earnings_per_share': -0.64, 'avg_profit_margin': -10.72}}, 'Health Care': {'202001': {'avg_revenue': 6002043857.14, 'avg_net_income': 445198285.71, 'avg_earnings_per_share': 1.47, 'avg_profit_margin': 13.01}, '202002': {'avg_revenue': 5581698714.29, 'avg_net_income': -15565285.71, 'avg_earnings_per_share': 2.41, 'avg_profit_margin': 0.19}, '202003': {'avg_revenue': 6331397428.57, 'avg_net_income': 406568142.86, 'avg_earnings_per_share': 2.66, 'avg_profit_margin': 25.76}, '202004': {'avg_revenue': 8299446400.0, 'avg_net_income': 575688600.0, 'avg_earnings_per_share': 1.08, 'avg_profit_margin': 55.16}, '202101': {'avg_revenue': 3239000000.0, 'avg_net_income': 656000000.0, 'avg_earnings_per_share': 4.46, 'avg_profit_margin': 20.25}}}

for sector, value in json_return.items():
    print(sector)
    for year_quarter, financials_dict in value.items():
        print(year_quarter)
        print('avg_revenue')
        print(financials_dict['avg_revenue'])
print('-' * 15)
print([year_quarter for year_quarter in json_return['Energy'].keys()])
print([(financials['avg_revenue']) for financials in json_return['Energy'].values()])

def get_time_n_financials_axis(sector, quarterly_financials, financial_item):
    x_axis_time_series = [year_quarter for year_quarter in json_return[sector].keys()]
    y_axis_financials = [(financials[financial_item]) for financials in json_return[sector].values()]
    return x_axis_time_series, y_axis_financials

for sector, quarterly_financials in json_return.items():
    print(sector)
    print('avg_revenue')
    x_axis_time_series, y_axis_financials = get_time_n_financials_axis(sector, quarterly_financials, 'avg_revenue')
    print(x_axis_time_series)
    print(y_axis_financials)
breakpoint()


# 05/01
# sub_industry.py
"""
needs to find the latest year-quarter among all the sectors, then 
set the cut-off quarter to be latest - 5
"""
sector_records_dict = {'Consumer Staples': {202101: {'avg_revenue': Decimal('22234742076.92'), 'avg_net_income': Decimal('613684230.77'), 'avg_earnings_per_share': Decimal('1.96'), 'avg_profit_margin': Decimal('10.39')}, 202004: {'avg_revenue': Decimal('13227184107.14'), 'avg_net_income': Decimal('992984642.86'), 'avg_earnings_per_share': Decimal('1.37'), 'avg_profit_margin': Decimal('14.80')}, 202003: {'avg_revenue': Decimal('13884618172.41'), 'avg_net_income': Decimal('975771379.31'), 'avg_earnings_per_share': Decimal('1.35'), 'avg_profit_margin': Decimal('12.56')}, 202002: {'avg_revenue': Decimal('12595588838.71'), 'avg_net_income': Decimal('569776967.74'), 'avg_earnings_per_share': Decimal('0.69'), 'avg_profit_margin': Decimal('8.52')}, 202001: {'avg_revenue': Decimal('12615849903.23'), 'avg_net_income': Decimal('780862806.45'), 'avg_earnings_per_share': Decimal('0.99'), 'avg_profit_margin': Decimal('12.73')}, 201904: {'avg_revenue': Decimal('6888409105.26'), 'avg_net_income': Decimal('544397421.05'), 'avg_earnings_per_share': Decimal('0.80'), 'avg_profit_margin': Decimal('8.36')}, 201903: {'avg_revenue': Decimal('2841600000.00'), 'avg_net_income': Decimal('-402800000.00'), 'avg_earnings_per_share': Decimal('-1.86'), 'avg_profit_margin': Decimal('-14.18')}, 201902: {'avg_revenue': Decimal('2948300000.00'), 'avg_net_income': Decimal('329400000.00'), 'avg_earnings_per_share': Decimal('1.52'), 'avg_profit_margin': Decimal('11.17')}}, 'Health Care': {202101: {'avg_revenue': Decimal('3239000000.00'), 'avg_net_income': Decimal('656000000.00'), 'avg_earnings_per_share': Decimal('4.46'), 'avg_profit_margin': Decimal('20.25')}, 202004: {'avg_revenue': Decimal('8299446400.00'), 'avg_net_income': Decimal('575688600.00'), 'avg_earnings_per_share': Decimal('1.08'), 'avg_profit_margin': Decimal('55.16')}, 202003: {'avg_revenue': Decimal('6331397428.57'), 'avg_net_income': Decimal('406568142.86'), 'avg_earnings_per_share': Decimal('2.66'), 'avg_profit_margin': Decimal('25.76')}, 202002: {'avg_revenue': Decimal('5581698714.29'), 'avg_net_income': Decimal('-15565285.71'), 'avg_earnings_per_share': Decimal('2.41'), 'avg_profit_margin': Decimal('0.19')}, 202001: {'avg_revenue': Decimal('6002043857.14'), 'avg_net_income': Decimal('445198285.71'), 'avg_earnings_per_share': Decimal('1.47'), 'avg_profit_margin': Decimal('13.01')}, 201904: {'avg_revenue': Decimal('5824841000.00'), 'avg_net_income': Decimal('760636857.14'), 'avg_earnings_per_share': Decimal('2.21'), 'avg_profit_margin': Decimal('22.11')}, 201903: {'avg_revenue': Decimal('2508767000.00'), 'avg_net_income': Decimal('140557000.00'), 'avg_earnings_per_share': Decimal('0.95'), 'avg_profit_margin': Decimal('5.60')}}, 'Energy': {202004: {'avg_revenue': Decimal('8597901000.00'), 'avg_net_income': Decimal('-1214363888.89'), 'avg_earnings_per_share': Decimal('-0.64'), 'avg_profit_margin': Decimal('-10.72')}, 202003: {'avg_revenue': Decimal('7909252736.84'), 'avg_net_income': Decimal('-231239578.95'), 'avg_earnings_per_share': Decimal('-0.68'), 'avg_profit_margin': Decimal('-11.32')}, 202002: {'avg_revenue': Decimal('5641133850.00'), 'avg_net_income': Decimal('-1358037000.00'), 'avg_earnings_per_share': Decimal('-1.97'), 'avg_profit_margin': Decimal('-74.09')}, 202001: {'avg_revenue': Decimal('10069083000.00'), 'avg_net_income': Decimal('-1516083350.00'), 'avg_earnings_per_share': Decimal('-2.71'), 'avg_profit_margin': Decimal('-33.63')}, 201904: {'avg_revenue': Decimal('12000061800.00'), 'avg_net_income': Decimal('-4031150.00'), 'avg_earnings_per_share': Decimal('-0.08'), 'avg_profit_margin': Decimal('-5.08')}, 201903: {'avg_revenue': Decimal('5687000000.00'), 'avg_net_income': Decimal('-794000000.00'), 'avg_earnings_per_share': Decimal('-1.08'), 'avg_profit_margin': Decimal('-13.96')}, 201902: {'avg_revenue': Decimal('4420000000.00'), 'avg_net_income': Decimal('635000000.00'), 'avg_earnings_per_share': Decimal('0.85'), 'avg_profit_margin': Decimal('14.37')}}}
print(sector_records_dict.keys())
print(sector_records_dict['Energy'])
print(max(sector_records_dict['Energy'].keys()))
print(list(sector_records_dict['Energy'].keys())[:5])
print([(key, max(sector_records_dict[key].keys()), sector_records_dict[key].keys()) for key in sector_records_dict.keys()])
print(max([max(sector_records_dict[key].keys()) for key in sector_records_dict.keys()]))
print(max({max(sector_records_dict[key].keys()):key for key in sector_records_dict.keys()}))
most_recent_quarter = max([max(sector_records_dict[key].keys()) for key in sector_records_dict.keys()])
for value in sector_records_dict.values():
    if most_recent_quarter not in value.keys():
        continue
    else:
        most_recent_quarters = list(value.keys())[:5]
        print(most_recent_quarters)
        break
print(most_recent_quarters) 

def get_uniform_length_dicts(dict_of_dicts:dict, uniform_length=5):
    most_recent_quarters = get_most_recent_quarters(dict_of_dicts, uniform_length)
    for sector, quarterly_records_dict in dict_of_dicts.items():
        dict_of_dicts[sector] = {key:value for key, value in quarterly_records_dict.items()
                                                                    if key in most_recent_quarters}
    return dict_of_dicts

def get_most_recent_quarters(dict_of_dicts, uniform_length):
    most_recent_quarter = max([max(sector_records_dict[key].keys()) 
                                            for key in sector_records_dict.keys()])
    for sector_quarterly_records in dict_of_dicts.values():
        if most_recent_quarter not in sector_quarterly_records.keys(): continue
        else:
            most_recent_quarters = list(sector_quarterly_records.keys())[:uniform_length]
            break
    return most_recent_quarters

uniformed_dicts = get_uniform_length_dicts(sector_records_dict)

for sector in uniformed_dicts:
    print(uniformed_dicts[sector])
    print('-' * 15)
breakpoint()

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