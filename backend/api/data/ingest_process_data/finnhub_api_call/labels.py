import re
import pandas as pd
import finnhub
import datetime
import pytz
from api.data.ingest_process_data.helpers import finnhub_client
from api.data.ingest_process_data.finnhubAPI_calls.fin_statement_items_variations import FinStatementItemName

def company_historical_financials(ticker:str, 
                                  frequency = 'quarterly', 
                                  finnhub_client = finnhub_client):
    """
    params: ticker -> stock's ticker symbol
            frequency -> 'quarterly' or 'annual'
    returns a list of quarterly statements by the API call.
    """
    quarterly_statements = finnhub_client().financials_reported(symbol=ticker, freq= frequency)
    return quarterly_statements

def quarterly_statements_labels(ticker: str, number_of_quarters= 16):
    """
    Quarterly info available from API calls dates back to year 2017.
    """
    quarterly_statements_list = company_historical_financials(ticker)['data']
    quarter_statements_labels = {}
    for i, quarterly_statements in enumerate(quarterly_statements_list):
        if i > number_of_quarters:
            break
        else:
            quarter_endDate = quarterly_statements['endDate'].split(' ')[0]
            quarter_stamp = f"{quarter_endDate} {ticker}"
            quarter_statements_labels[quarter_stamp] = {}
            quarterly_labels_data = quarter_statements_labels[quarter_stamp]
            quarterly_labels_data['labels'] = [fin_item['label'] for fin_item in 
                                                                    quarterly_statements['report']['ic']]
            quarterly_labels_data['quarter_fin_statements'] = quarterly_statements
    return quarter_statements_labels

def single_quarter_ic_labels_values(quarterly_statements):
    """
    returns a dictionary of the quarter's labels (financial statements items) and 
    their corresponding values.
    """
    ticker = quarterly_statements['symbol']
    quarter_endDate = quarterly_statements['endDate'].split(' ')[0]
    quarter_number = f" Q{quarterly_statements['quarter']}"
    quarter_stamp = ticker + quarter_number + ' ' + quarter_endDate

    quarter_labels_values = {}
    labels_values_pairs = {fin_item['label']: fin_item['value'] for fin_item in 
                                                                quarterly_statements['report']['ic']}
    quarter_labels_values[quarter_stamp] = labels_values_pairs
    return quarter_labels_values

### to be imported by regex_parsing.py
