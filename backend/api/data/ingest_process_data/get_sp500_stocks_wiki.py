"""
This script needs to be run from the root level of the backend/ folder.
"""

import pandas as pd 

sp500_df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
sp500_df.to_csv("./api/data/sp500/raw_data/sp500_stocks_wiki_info.csv")