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
from collections import Counter

sector_counter = Counter()
sub_industry_counter = {}
with open("../sp500/raw_data/sp500_stocks_info.csv") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        if row['GICS Sector'] not in sector_counter:
            sub_industry_counter[row['GICS Sector']] = Counter()  
        sector_counter[row['GICS Sector']] += 1
        sub_industry_counter[row['GICS Sector']][
                                                row['GICS Sub-Industry']] += 1

# In[ ]:


sectors_str = ", ".join(sector_counter.keys()) # Pandas series
sectors_str


# In[ ]:


with open('../sp500/processed_data/sectors_str.csv', 'w') as writer:
    writer.write(sectors_str)


# In[ ]:
sub_industries_dict = {key:[k for k in value.keys()] for key, value in sub_industry_counter.items()}
sub_industries_json = json.dumps(sub_industries_dict, default = str)


# In[ ]:


with open('../sp500/processed_data/sub_industries.json', 'w') as writer:
    writer.write(sub_industries_json)

