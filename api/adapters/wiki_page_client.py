import pandas as pd
import os

class WikiPageClient:
    def __init__(self):
        self.sp500_wiki_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        self.data_dir = './api/data/sp500/raw_data'
        self._ensure_data_directory()

    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)

    def get_sp500_wiki_data(self):
        """Scrape S&P 500 companies data from Wikipedia"""
        tables = pd.read_html(self.sp500_wiki_url)
        df = tables[0]
        df.to_csv(f'{self.data_dir}/sp500_stocks_wiki_info.csv', index=False)
        return df
