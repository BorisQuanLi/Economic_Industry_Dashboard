#!/usr/bin/env python
# coding: utf-8

# Obtain data for the CompanyBuilder class, Jigsaw_DE/Python-SQL-Dashboard-project/api/src/adapters/companies_builder.py


import intrinio_sdk as intrinio
from intrinio_sdk.rest import ApiException
from api.data.ingest_process_data.helpers import activate_intrinio_api
import csv

# from read_dow_jones_tickers import *


def via_intrinio_api(ticker, api_activation = activate_intrinio_api()):
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
