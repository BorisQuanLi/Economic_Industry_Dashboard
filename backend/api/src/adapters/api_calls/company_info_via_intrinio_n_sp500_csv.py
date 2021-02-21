#!/usr/bin/env python
# coding: utf-8

# Obtain data for the CompanyBuilder class, Jigsaw_DE/Python-SQL-Dashboard-project/api/src/adapters/companies_builder.py


import intrinio_sdk as intrinio
from intrinio_sdk.rest import ApiException
from api.src.adapters.api_calls.helpers import activate_intrinio_api
import csv

# from read_dow_jones_tickers import *


def company_info_via_intrinio_api_n_sp500_csv(ticker:str, 
                                              filepath= './data/sp500/S&P500-Info.csv'):
    def company_info_via_intrinio(ticker, api_activation = activate_intrinio_api()):
        """
        https://docs.intrinio.com/documentation/python/get_company_v2
        """
        identifier = ticker
        try:
            intrinio.CompanyApi().get_company(identifier)
            company_lookup = intrinio.CompanyApi().get_company(identifier)
            company_info_dict = {'name': company_lookup.legal_name,
                             'ticker': company_lookup.ticker,
                             'number_of_employees': company_lookup.employees,
                             'HQ_state': company_lookup.hq_state,
                             'country': company_lookup.hq_country,
                             }
        except Exception as e:
            unavailable_company_info = (ticker, e)
            return unavailable_company_info
        
        return company_info_dict

    def company_info_via_sp500_csv(ticker, company_dict,
                                   filepath= 'api/data/sp500/S&P500-Info.csv'):
        """
        param ticker: string
        """
        with open(filepath) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['Symbol'] == ticker:
                    company_dict['year_founded'] = row['Founded']
                    company_dict['sub_industry_name'] = row['GICS Sub-Industry']
        return company_dict

    company_dict_from_intrinio = company_info_via_intrinio(ticker)
    if type(company_dict_from_intrinio) != dict:
        return {f'{ticker} info not avaiable from Intrinio' : company_dict_from_intrinio}
    else:
        company_dict = company_info_via_sp500_csv(ticker, company_dict_from_intrinio)
        return company_dict


def companies_info_via_intrinio_api_n_sp500_csv(tickers_list):
    companies_info_list = []
    for ticker in tickers_list:
        companies_info_list.append(
                                company_info_via_intrinio_api_n_sp500_csv(ticker))
    return companies_info_list



apple_sub_industry_companies = ['HPE', 'NTAP', 'STX', 'WDC']
companies_info_apple_sub_industry = (
                    companies_info_via_intrinio_api_n_sp500_csv(
                                    apple_sub_industry_companies))
companies_info_apple_sub_industry

