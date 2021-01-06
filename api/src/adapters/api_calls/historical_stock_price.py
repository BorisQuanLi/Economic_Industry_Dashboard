#!/usr/bin/env python
# coding: utf-8

import intrinio_sdk as intrinio
from intrinio_sdk.rest import ApiException
import datetime
import pytz
from .helpers import activate_intrinio_api, most_recent_busines_day_eastern
# from read_dow_jones_tickers import *


def historical_price(ticker, date, intrinio_api = activate_intrinio_api()):
    """
    params: ticker -> string, date -> string 'yyyy-mm-dd'
    
    As of 01/03/2020, the earliest date when stock quote is available
    from intrinio is 10/12/2020, which works at the current stage 
    of developing the S&P 500 investment analysis project in the
    Jigsaw Labs course on Python-SQL-dashboard.
    """
    identifier = ticker
    start_date = ''
    end_date = date
    frequency = 'daily'
    page_size = 1
    next_page = ''

    response = intrinio.SecurityApi().get_security_stock_prices(identifier, 
                            start_date=start_date, end_date=end_date, frequency=frequency, page_size=page_size, next_page=next_page)

    return response.stock_prices[0].close, response.stock_prices[0].date


# stock_historical_price_via_intrinio_api('IBM', '2020-09-30')






