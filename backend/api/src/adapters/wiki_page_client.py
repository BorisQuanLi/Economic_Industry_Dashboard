#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

def get_sp500_wiki_data():
    """
    Scrapes S&P 500 company data from Wikipedia
    Returns DataFrame with company info and proper column names
    """
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table', {'id': 'constituents'})
    return pd.read_html(str(table))[0]

def get_sp500_wiki_info():
    """ingest each and every S&P 500 company's basic info from the Wikipedia web page"""
    sp500_df = get_sp500_wiki_data()
    column_names = list(sp500_df.columns)
    column_names[0] = 'Ticker'
    sp500_df.columns = column_names
    return sp500_df

def get_employees_total():
    """ ingest each company's total number of employees """
    returned_dataframes = pd.read_html('https://www.liberatedstocktrader.com/sp-500-companies-list-by-number-of-employees/')
    employees_total = returned_dataframes[2]
    employees_total_df = employees_total.iloc[1:, 1:].copy()
    employees_total_df.columns = employees_total.iloc[0, 1:]
    return employees_total_df

def merge_df(sp500_df, employees_total_df):
    # merge the two dataframes
    sp500_incl_employees_df = pd.merge(sp500_df, employees_total_df, 
                                      on='Ticker', how='outer')
    sp500_incl_employees_df['Employees'].fillna(-1, inplace=True)
    security_col_notna = sp500_incl_employees_df['Security'].notna()
    sp500_incl_employees_df = sp500_incl_employees_df[security_col_notna]
    return sp500_incl_employees_df

def save_csv(sp500_incl_employees_df, sp500_wiki_data_filepath):
    # save the merged dataframe in a csv file
    sp500_incl_employees_df.to_csv(sp500_wiki_data_filepath)
    return sp500_wiki_data_filepath

def ingest_sp500_stocks_info():
    """Extracts S&P 500 companies' basic information"""
    sp500_wiki_data_filepath = "./backend/api/data/sp500/raw_data/sp500_stocks_wiki_info.csv"
    os.makedirs(os.path.dirname(sp500_wiki_data_filepath), exist_ok=True)
    with open(sp500_wiki_data_filepath) as existing_file:
        if not existing_file:
            sp500_df = get_sp500_wiki_data()
            employees_total_df = get_employees_total()
            sp500_incl_employees_df = merge_df(sp500_df, employees_total_df)
            sp500_wiki_data_filepath = save_csv(sp500_incl_employees_df, sp500_wiki_data_filepath)
    return sp500_wiki_data_filepath

__all__ = ['get_sp500_wiki_data', 'get_sp500_wiki_info', 'ingest_sp500_stocks_info']

if __name__ == "__main__":
    ingest_sp500_stocks_info()
