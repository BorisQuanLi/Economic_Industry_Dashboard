#!/usr/bin/env python
# coding: utf-8

import os
import glob
import logging
from datetime import datetime
from io import StringIO

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

def get_wiki_data_filepath():
    """Calculates the dynamic quarterly filepath for the S&P 500 data."""
    now = datetime.now()
    current_q = (now.month - 1) // 3 + 1
    quarter_suffix = f"{now.year}_{current_q}q"
    
    base_dir = os.getenv("DATA_DIR", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(base_dir, "data", f"sp500_stocks_wiki_info_{quarter_suffix}.csv")

# Initialize the constant at module level by calling the function
WIKI_DATA_FILEPATH = get_wiki_data_filepath()

# Mimic a standard browser session to prevent 403 (Forbidden) responses.
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_sp500_wiki_data():
    """
    Extracts S&P 500 companies' basic information from Wikipedia.
    Saves the combined info in a CSV file. 
    Returns the CSV file's absolute path.
    """

    if not os.path.exists(WIKI_DATA_FILEPATH):
        # Run cleanup before generating new data
        cleanup_old_quarters(WIKI_DATA_FILEPATH)
        
        os.makedirs(os.path.dirname(WIKI_DATA_FILEPATH), exist_ok=True)
        
        # Get foundational dataset
        sp500_df = get_sp500_wiki_info()

        # Get total number of employees of each company
        sp500_with_employees_total_df  = include_employees_total(sp500_df)
                    
        # Persist the Pandas DataFrame in csv file
        save_csv(sp500_with_employees_total_df , WIKI_DATA_FILEPATH)
        logger.info(f"Data saved to {WIKI_DATA_FILEPATH}")

    return os.path.abspath(WIKI_DATA_FILEPATH)

def get_sp500_wiki_info():
    """Ingest S&P 500 company basic info from Wikipedia."""
    url = 'https://en.wikipedia.org'
    session = get_session_with_retries()
    response = session.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    # Use StringIO to avoid FutureWarning from read_html
    tables = pd.read_html(StringIO(response.text))
    if not tables:
        raise ValueError("No tables found on Wikipedia S&P 500 page")

    sp500_df = tables[0]
    # Rename 'Symbol' column to 'Ticker' for consistency across data sources
    return sp500_df.rename(columns={'Symbol': 'Ticker'})

def include_employees_total(sp500_df):
    """
    Integrates mandatory employee count data into the S&P 500 DataFrame.
    Inlines extraction logic to simplify the module structure.
    """
    url = 'https://www.liberatedstocktrader.com/sp-500-companies-list-by-number-of-employees/'
    
    try:
        session = get_session_with_retries()
        response = session.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        
        returned_dataframes = pd.read_html(StringIO(response.text))
        employees_total = returned_dataframes[0]
        
        # Clean and format the raw scraped table
        employees_total_df = employees_total.iloc[1:, 1:].copy()
        employees_total_df.columns = employees_total.iloc[0, 1:]
        
        return merge_df(sp500_df, employees_total_df)

    except Exception as e:
        logger.error(f"Mandatory employee data extraction failed: {e}. Using fallback values.")
        final_df = sp500_df.copy()
        if 'Employees' not in final_df.columns:
            final_df['Employees'] = -1
        return final_df

def merge_df(sp500_df, employees_total_df):
    # merge the two dataframes
    sp500_with_employees_total_df  = pd.merge(sp500_df, employees_total_df, 
                                        on= 'Ticker', how='outer')
    sp500_with_employees_total_df ['Employees'].fillna(-1, inplace= True)
    security_col_notna = sp500_with_employees_total_df ['Security'].notna()
    sp500_with_employees_total_df  = sp500_with_employees_total_df [security_col_notna]
    return sp500_with_employees_total_df 

def get_session_with_retries():
    """Create a requests session with retry logic for resilient network calls."""
    session = requests.Session()
    # Retry on common transient server errors (500, 502, 503, 504)
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session

def save_csv(df, target_filepath):
    """Save the dataframe to a CSV file. Fixes the NameError."""
    os.makedirs(os.path.dirname(target_filepath), exist_ok=True)
    df.to_csv(target_filepath, index=False)

def cleanup_old_quarters(current_filepath):
    """Removes any old S&P 500 CSV files to keep the data directory tidy."""
    data_dir = os.path.dirname(current_filepath)
    # Search for all CSVs matching the pattern
    pattern = os.path.join(data_dir, "sp500_stocks_wiki_info_*.csv")
    for old_file in glob.glob(pattern):
        if old_file != current_filepath:
            try:
                os.remove(old_file)
                logger.info(f"Removed outdated data file: {old_file}")
            except OSError as e:
                logger.warning(f"Failed to delete old file {old_file}: {e}")

if __name__ == "__main__":
    ingest_sp500_stocks_info() 
