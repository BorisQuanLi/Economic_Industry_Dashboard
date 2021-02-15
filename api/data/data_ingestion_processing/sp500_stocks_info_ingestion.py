#!/usr/bin/env python
# coding: utf-8

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

# In[ ]:


import pandas as pd
from collections import Counter
import csv


# In[ ]:


sp500_df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]


# In[ ]:


sp500_df.head()


# In[ ]:


sp500_df.to_csv("../sp500/raw_data/sp500_stocks.csv")


# In[ ]:


sector_counter = Counter()
sub_industry_counter = {}
with open("../sp500/raw_data/sp500_stocks.csv") as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        if row['GICS Sector'] not in sector_counter:
            sub_industry_counter[row['GICS Sector']] = Counter()  
        sector_counter[row['GICS Sector']] += 1
        sub_industry_counter[row['GICS Sector']][
                                                row['GICS Sub-Industry']] += 1


# In[ ]:


sector_counter


# In[ ]:


sectors_str = ", ".join(sector_counter.keys()) # Pandas series
sectors_str


# In[ ]:


with open('../sp500/processed_data/sectors.csv', 'w') as writer:
    writer.write(sectors_str)


# In[ ]:


sub_industry_counter


# In[ ]:


sub_industries_string = ", ".join([", ".join(counter.keys()) 
                                                   for counter in sub_industry_counter.values()])
sub_industries_string


# In[ ]:


with open('../sp500/processed_data/sectors.csv', 'w') as writer:
    writer.write(sectors_str)

