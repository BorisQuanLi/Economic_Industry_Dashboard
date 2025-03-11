import pandas as pd

class WikiPageClient:
    def __init__(self):
        self.data_path = './backend/api/data/sp500/raw_data/sp500_stocks_wiki_info.csv'

    def get_sp500_wiki_data(self):
        return pd.read_csv(self.data_path)
