#!/usr/bin/env python
# coding: utf-8


import os
import pandas as pd
import requests

def ingest_sp500_stocks_info():
    """
    Extracts from two web sites the S&P 500 companies' basic information. such as name, ticker symbol.
    
    Save the combined info in a csv file. 

    Returns the csv file's absolute file path from the root level of the backend folder.

    To be executed from the root level of the /backend directory:

    backend$ python3 api/data/ingest_process_data/ingest_sp500_wiki_info_employees_total.py
    """

    sp500_wiki_data_filepath = "./api/data/sp500/raw_data/sp500_stocks_wiki_info.csv"
    import os
    if not os.path.exists(sp500_wiki_data_filepath):
        sp500_df = get_sp500_wiki_info()
        employees_total_df = get_employees_total()
        sp500_incl_employees_df = merge_df(sp500_df, employees_total_df)
        sp500_wiki_data_filepath = save_csv(sp500_incl_employees_df, sp500_wiki_data_filepath)
    return sp500_wiki_data_filepath

import requests

def get_sp500_wiki_info():
    """ingest each and every S&P 500 company's basic info from the Wikipedia web page"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url, headers=headers)
    sp500_df = pd.read_html(response.text)[0]
    column_names = list(sp500_df.columns)
    column_names[0] = 'Ticker'
    sp500_df.columns = column_names
    return sp500_df

def get_employees_total():
    """ ingest each company's total number of employees """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    url = 'https://www.liberatedstocktrader.com/sp-500-companies-list-by-number-of-employees/'
    response = requests.get(url, headers=headers)
    returned_dataframes = pd.read_html(response.text)
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
