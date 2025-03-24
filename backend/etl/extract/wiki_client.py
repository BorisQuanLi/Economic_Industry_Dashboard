import pandas as pd
import os

class WikipediaDataIngestionClient:
    def ingest_sp500_company_info(self) -> str:
        """
        Ingest S&P 500 company information from Wikipedia and persist to CSV.
        
        Fetches company metadata including ticker symbols, names, and GICS sector/industry
        classifications from the S&P 500 listing on Wikipedia.
        
        Returns:
            str: Path to the persisted CSV file
        """
        url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
        tables = pd.read_html(url)
        df = tables[0]  # First table contains S&P 500 companies

        # Define the directory and file path
        module_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current module
        data_dir = os.path.join(module_dir, 'data', 'raw', 'sp500')
        csv_filepath = os.path.join(data_dir, 'sp500_stocks_wiki_info.csv')

        # Create the directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)

        # Save the DataFrame to CSV
        df.to_csv(csv_filepath, index=False)

        return csv_filepath
