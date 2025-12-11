#!/usr/bin/env python
# coding: utf-8

import os
import time
import logging
from io import StringIO

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

def get_session_with_retries():
    """Create a requests session with retry logic."""
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_sp500_wiki_data():
    """
    Extracts S&P 500 companies' basic information from Wikipedia.
    Save the combined info in a csv file. 
    Returns the csv file's absolute file path.
    """
    sp500_wiki_data_filepath = "/app/data/sp500_stocks_wiki_info.csv"
    if not os.path.exists(sp500_wiki_data_filepath):
        os.makedirs(os.path.dirname(sp500_wiki_data_filepath), exist_ok=True)
        sp500_df = get_sp500_wiki_info()
        
        # Try to get employees data, but continue without it if it fails
        try:
            employees_total_df = get_employees_total()
            sp500_incl_employees_df = merge_df(sp500_df, employees_total_df)
        except Exception as e:
            logger.warning(f"Could not fetch employees data: {e}. Continuing without it.")
            sp500_incl_employees_df = sp500_df
            sp500_incl_employees_df['Employees'] = -1
            
        sp500_wiki_data_filepath = save_csv(sp500_incl_employees_df, sp500_wiki_data_filepath)
    return sp500_wiki_data_filepath


# Alias for backward compatibility
ingest_sp500_stocks_info = get_sp500_wiki_data


def get_sp500_wiki_info():
    """Ingest S&P 500 company basic info from Wikipedia."""
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    session = get_session_with_retries()
    response = session.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    
    # Use StringIO to avoid FutureWarning
    tables = pd.read_html(StringIO(response.text))
    if not tables:
        raise ValueError("No tables found on Wikipedia S&P 500 page")
    
    sp500_df = tables[0]
    # Rename 'Symbol' column to 'Ticker' for consistency
    sp500_df = sp500_df.rename(columns={'Symbol': 'Ticker'})
    return sp500_df


def get_employees_total():
    """Ingest each company's total number of employees."""
    url = 'https://www.liberatedstocktrader.com/sp-500-companies-list-by-number-of-employees/'
    session = get_session_with_retries()
    response = session.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    
    returned_dataframes = pd.read_html(StringIO(response.text))
    employees_total = returned_dataframes[0]
    employees_total_df = employees_total.iloc[1:, 1:].copy()
    employees_total_df.columns = employees_total.iloc[0, 1:]
    return employees_total_df

def merge_df(sp500_df, employees_total_df):
    # merge the two dataframes
    sp500_incl_employees_df = pd.merge(sp500_df, employees_total_df, 
                                        on= 'Ticker', how='outer')
    sp500_incl_employees_df['Employees'].fillna(-1, inplace= True)
    security_col_notna = sp500_incl_employees_df['Security'].notna()
    sp500_incl_employees_df = sp500_incl_employees_df[security_col_notna]
    return sp500_incl_employees_df

def save_csv(sp500_incl_employees_df, filepath):
    """Save the dataframe to a CSV file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    sp500_incl_employees_df.to_csv(filepath)
    return filepath

if __name__ == "__main__":
    ingest_sp500_stocks_info() 
