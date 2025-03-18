import pandas as pd
import os

class WikiPageClient:
    def extract_sp500_data(self):
        """Extract S&P 500 companies data from Wikipedia and save to CSV."""
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        df = tables[0]  # First table contains S&P 500 companies

        # Define the directory and file path
        extract_dir = os.path.dirname(os.path.abspath(__file__)) # Get the directory of the current script
        data_dir = os.path.join(extract_dir, 'data', 'raw', 'sp500')
        csv_filepath = os.path.join(data_dir, 'sp500_stocks_wiki_info.csv')

        # Create the directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)

        # Save the DataFrame to CSV
        df.to_csv(csv_filepath, index=False)

        return df
