#!/usr/bin/env python
# coding: utf-8


import pandas as pd

def ingest_sp500_stocks_info():
    """
    Ingests companies information of the S&P 500 Index components from two web resources.
    
    Save the info in a csv file. 
    Returns the csv file's absolute filepath from the root level of the backend folder.

    To be executed from the root level of the /backend dicectory:
    backend$ python3 api/data/ingest_process_data/ingest_sp500_wiki_info_employees_total.py
    """
    
    # ingest each S&P500 company's basic info from Wikipedia
    sp500_df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    column_names = list(sp500_df.columns)
    column_names[0] = 'Ticker'
    sp500_df.columns = column_names

    # ingest each company's total number of employees
    returned_dataframes = pd.read_html('https://www.liberatedstocktrader.com/sp-500-companies-list-by-number-of-employees/')
    employees_total = returned_dataframes[2]
    employees_total_df = employees_total.iloc[1:, 1:].copy()
    employees_total_df.columns = employees_total.iloc[0, 1:]
    
    # merge the two dataframes
    sp500_incl_employees_df = pd.merge(sp500_df, employees_total_df, 
                                        on= 'Ticker', how='outer')
    sp500_incl_employees_df['Employees'].fillna(-1, inplace= True)

    # save the merged dataframe in a csv file
    sp500_incl_employees_df.to_csv("./api/data/sp500/raw_data/sp500_stocks_wiki_info.csv")
    sp500_wiki_data_filepath = "./api/data/sp500/raw_data/sp500_stocks_wiki_info.csv"
    return sp500_wiki_data_filepath

if __name__ == "__main__":
    ingest_sp500_stocks_info() 
