"""
Needs to be run from the current folder.
"""

import csv
from collections import Counter

sectors_dict = Counter()
with open ('../api/data/sp500/S&P500-Info.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        sectors_dict[row['GICS Sector']] += 1
sector_name_industrials = list(sectors_dict.keys())[0]

sectors_dict[f'{sector_name_industrials}'] = Counter()
industrials_sub_industries_dict = sectors_dict[f'{sector_name_industrials}']
with open ('../api/data/sp500/S&P500-Info.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        if row['GICS Sector'] == sector_name_industrials:
            industrials_sub_industries_dict[row['GICS Sub-Industry']] += 1

industrials_airlines_companies_dict = Counter()
with open('../api/data/sp500/S&P500-Info.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        if (row['GICS Sector'] == f'{sector_name_industrials}' 
                and row['GICS Sub-Industry'] == 'Airlines'):
                industrials_airlines_companies_dict[row['Security']] += 1


# find the row of 'United Airlines Holdings'
with open('../api/data/sp500/S&P500-Info.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        if row['Security'] == 'United Airlines Holdings':
            united_airlines_row = row


united_airlines_dict = united_airlines_row
# simplify the data import
sp500_row_fields_company_columns_dict = {'Security': 'name',
                                        'Symbol': 'ticker',
                                        'sub_industry_id': 'sub_industry_id',
                                        'Founded': 'year_founded'}
united_airlines_dict= {sp500_row_fields_company_columns_dict[key]:value 
                            for key,value in united_airlines_dict.items() 
                                if key in sp500_row_fields_company_columns_dict}


print(sectors_dict)
print(industrials_sub_industries_dict)
print(industrials_airlines_companies_dict)
print(united_airlines_row)
print(sp500_row_fields_company_columns_dict)
breakpoint()