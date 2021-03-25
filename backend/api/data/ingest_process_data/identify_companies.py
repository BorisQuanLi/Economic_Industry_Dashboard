# 02/14/2021
# 
# To be run in the /data_ingestion folder in this directory structure:
# /data/
#     /sp500/processed_data
#             sectors.csv
#             sub_industries.csv
#     /sp500/raw_data
#     
#     /ingestion_scripts/
#         sp500_stocks_info_ingestion.py
#         
# --
# 
# Other than the initial reading of the two tables in the Wikipedia page, the data processing part of the script avoided using Pandas.
# 
# The idea is to become skillful in using the various basic Python data types and data structures.  


import csv
import json
from collections import defaultdict

companies_by_sub_industry = defaultdict(list)
with open("../sp500/raw_data/sp500_stocks_info.csv") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        if row['GICS Sub-Industry'] not in companies_by_sub_industry[
                                                                    row['GICS Sub-Industry']]:
            companies_by_sub_industry[row['GICS Sub-Industry']].append(row)

json_str = json.dumps(companies_by_sub_industry)
with open('../sp500/processed_data/companies_by_sub_industry.json', 'w') as writer:
    writer.write(json_str)
