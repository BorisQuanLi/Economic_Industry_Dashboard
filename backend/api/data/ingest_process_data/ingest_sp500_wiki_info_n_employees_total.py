#!/usr/bin/env python
# coding: utf-8

# to be executed from the root level of the /backend dicectory

import pandas as pd

def get_sp500_stocks_wiki_filepath():
    """
    Ingests companies information of the S&P 500 Index components from two web resources.
    Export the csv file to the designed data/ sub-folder, and returns its absolute
    filepath from the root level of the /backend folder.

    backend$ python3 api/data/ingest_process_data/ingest_sp500_wiki_info_employees_total.py
    """
    sp500_df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    
    employees_df = pd.read_html('https://www.liberatedstocktrader.com/sp-500-companies-list-by-number-of-employees/')
    employee_total_df = employees_df[1].iloc[1:, [1,5]]
    employee_total_df.columns = ['Ticker', '# Employees']
    employee_total_df['# Employees'].fillna('N/A', inplace= True)
    sp500_incl_employees_df = pd.merge(sp500_df, employee_total_df, left_on= 'Symbol', right_on= 'Ticker')
    sp500_incl_employees_df.drop('Ticker', axis=1, inplace=True)
    sp500_incl_employees_df.to_csv("./api/data/sp500/raw_data/sp500_stocks_wiki_info.csv")
    sp500_wiki_data_filepath = "./api/data/sp500/raw_data/sp500_stocks_wiki_info.csv"
    return sp500_wiki_data_filepath

if __name__ == "__main__":
    get_sp500_stocks_wiki_filepath() 
