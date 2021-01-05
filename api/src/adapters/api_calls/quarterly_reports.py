#!/usr/bin/env python
# coding: utf-8

# Original notebook: obtaining Quarterly Reports data, revenue, cost, net income, earnings per share, via Intrinio get_company_historical_data method, 01-04-2020

# from . import get_multiple_quarters_financials 

import intrinio_sdk as intrinio
from intrinio_sdk.rest import ApiException
from .helpers import activate_intrinio_api
import datetime
import pytz
from .helpers import *


def get_multiple_quarters_single_financial(ticker, tag, 
                                end_date = '2021-01-01',
                                frequency = 'quarterly',
                                number_of_quarters = 4,
                                api_activation = activate_intrinio_api()):
    """
    https://docs.intrinio.com/documentation/python/get_company_historical_data_v2
    """
    identifier = ticker
    tag = tag # 'marketcap'
    frequency = frequency
    type = ''
    start_date = ''
    end_date = end_date
    sort_order = 'desc'
    page_size = number_of_quarters
    next_page = ''
    response = intrinio.CompanyApi().get_company_historical_data(identifier, tag, frequency=frequency, type=type, start_date=start_date, end_date=end_date, sort_order=sort_order, page_size=page_size, next_page=next_page)
    mutliple_quarters_single_financial = [
            (datetime.datetime.strftime(qtr.date, '%Y-%m-%d'), qtr.value)
                                     for qtr in response.historical_data]
    return tag, mutliple_quarters_single_financial


def transpose_financials_matrix(multiple_quarters_financials):
    """
    https://www.geeksforgeeks.org/transpose-matrix-single-line-python/
    """
    financials_vector = [row[0] for row in multiple_quarters_financials]
    matrix = [row[1] for row in multiple_quarters_financials]
    transposed_matrix = [row for row in zip(*matrix)]
    quarterly_financials_list = []
    for row in transposed_matrix:
        quarterly_financials_dict = {}
        for financial, month_value in zip(financials_vector,row):
            financial_figure = month_value[1]
            quarterly_financials_dict[financial] = financial_figure
        quarterly_report_date = month_value[0]
        quarterly_financials_list.append(
                    (quarterly_report_date, quarterly_financials_dict))
    return quarterly_financials_list


def get_multiple_quarters_financials(ticker, 
                                    end_date = '2021-01-01',
                                    number_of_quarters = 4,
                                    api_activation = activate_intrinio_api()):
    sp500_project_financials = ['totalrevenue',
                                'totalcostofrevenue',
                                'netincome',
                                'basiceps']
    multiple_quarters_financials = []
    for financial in sp500_project_financials:
        multiple_quarters_financials.append(
                    get_multiple_quarters_single_financial(ticker, financial))
    quarterly_financials_list = transpose_financials_matrix(
                                                multiple_quarters_financials)
    
    four_quarters_financials_list = [{'Total Revenue': qtr_tuple[1]['totalrevenue'],
                                    'Total Cost of Revenue': qtr_tuple[1]['totalcostofrevenue'],
                                    'Consolidated Net Income / (Loss)': qtr_tuple[1]['netincome'],
                                    'Basic Earnings per Share': qtr_tuple[1]['basiceps'],
                                    'date': qtr_tuple[0],
                                    'ticker': ticker} 
                                                         for qtr_tuple in quarterly_financials_list]
    return four_quarters_financials_list

def get_companies_multiple_quarters_financials(list_of_tickers,
                                                end_date = '2021-01-01',
                                                number_of_quarters = 4,
                                                api_activation = activate_intrinio_api()):
    list_of_multiple_quarters_financials = []
    for ticker in list_of_tickers:
        list_of_multiple_quarters_financials.append(
                    get_multiple_quarters_financials(ticker))
    return list_of_multiple_quarters_financials




