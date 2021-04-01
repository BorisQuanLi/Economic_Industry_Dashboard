import psycopg2
from urllib.request import urlopen
import json
from datetime import datetime, timedelta
import pytz
import csv
import pandas as pd
import pandas_market_calendars as mcal
import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters

class QuarterReportBuilder:
    financials_attributes = ['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share'] 
    prices_pe_attributes = ['date', 'company_id', 'closing_price', 'price_earnings_ratio']
    API_KEY = "f269391116fc672392f1a2d538e93171" # to be saved in .env

    def run(self, ticker, company_id, sector_name, conn, cursor):
        self.company_id = company_id
        self.conn = conn
        self.cursor = cursor
        if not db.find(models.QuarterlyReport, company_id, cursor):
            recent_five_quarterly_report_records = self.get_quarterly_financials(ticker)
            self.save_quarterly_financials_records(company_id, recent_five_quarterly_report_records)
            if not db.find(models.PricePE, company_id, cursor):
                self.save_price_pe_records(ticker, company_id, recent_five_quarterly_report_records)

    def get_quarterly_financials(self, ticker, api_key= API_KEY):
        response = urlopen(f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&apikey={api_key}")
        data = response.read().decode("utf-8")
        qtr_ic =  json.loads(data)
        recent_five_quarterly_report_records = qtr_ic[:5]
        return recent_five_quarterly_report_records

    def save_quarterly_financials_records(self, company_id, quarterly_ic_records):
        quarterly_reports_objs = []
        for quarterly_ic_record in quarterly_ic_records:
            quarterly_report_obj = self.save_quarterly_record(company_id, quarterly_ic_record)
            quarterly_reports_objs.append(quarterly_report_obj)
        return quarterly_reports_objs

    def save_quarterly_record(self, company_id, quarterly_ic_record):
        values_vector = self.get_financials_vector(quarterly_ic_record, company_id)
        quarter_report_dict = dict(zip(self.financials_attributes, values_vector))
        obj = models.QuarterlyReport(**quarter_report_dict)
        quarterly_report_obj = db.save(obj, self.conn, self.cursor)
        return quarterly_report_obj
    
    def get_financials_vector(self, quarterly_ic_record, company_id):
        values_vector = [quarterly_ic_record['date'],
                         company_id,
                         quarterly_ic_record['revenue'],
                         quarterly_ic_record['netIncome'],
                         round(quarterly_ic_record['eps'], 2)]
        return values_vector

    def save_price_pe_records(self, ticker, company_id, recent_five_quarterly_report_records):
        for quarterly_info_row in recent_five_quarterly_report_records:
            values_vector = self.get_price_pe_values_vector(ticker, company_id, quarterly_info_row)
            price_de_dict = dict(zip(self.prices_pe_attributes, values_vector))
            obj = models.PricePE(**price_de_dict)
            price_pe_obj = db.save(obj, self.conn, self.cursor)

    def get_price_pe_values_vector(self, ticker, company_id, quarterly_info_row):
        date, closing_price = self.get_quarter_closing_date_price(ticker, quarterly_info_row['date'])
        eps = quarterly_info_row['eps']
        p_e_ratio = closing_price / eps
        values_vector = [date, company_id, closing_price, p_e_ratio]
        return values_vector

    def get_quarter_closing_date_price(self, ticker:str, date_in_report:str):
        historical_prices_dict = self.get_stock_daily_prices(ticker)
        most_recent_day, closing_price = self.get_most_recent_price_available(date_in_report, 
                                                                              historical_prices_dict)
        return most_recent_day, closing_price

    def get_most_recent_price_available(self, date_in_report, historical_prices_dict):        
        most_recent_trading_day_found = False
        while not most_recent_trading_day_found:
            try:
                most_recent_trading_day = self.get_most_recent_busines_day_eastern(date_in_report)
                closing_price = round(historical_prices_dict[most_recent_trading_day], 2)
                most_recent_trading_day_found = True
            except:
                # move the date earlier by one business day
                date = self.get_most_recent_busines_day_eastern(date_in_report)
                continue
        return most_recent_trading_day, closing_price

    def get_stock_daily_prices(self, ticker:str, number_days=500):
        """
        Turn the list of a stock's daily closing prices, returned by the FMP api call,
        into a dictionary, with date as key, daily closing pricde as value.
        
        As of April 2021, going back 350 days to match the 5 quarters of Income Statement
        financials that were return by FMP api call with different parameters.
        """
        response = urlopen(f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?serietype=line&apikey={self.API_KEY}")
        data = response.read().decode("utf-8")
        all_historical_prices = json.loads(data)['historical']
        # get only the needed number of days of closing prices
        daily_historical_prices =  all_historical_prices[:number_days]
        historical_prices_dict = {day['date']: day['close']
                                                        for day in daily_historical_prices}
        return historical_prices_dict

    def get_most_recent_busines_day_eastern(self, date:str, business_days_delta=1):
        date_in_datetime = datetime.strptime(date, "%Y-%m-%d")
        date_eastern = date_in_datetime.astimezone(
                                                pytz.timezone('US/Eastern')).date()
        date_df = pd.DataFrame(dict(
                                    timestamp=pd.to_datetime([date_eastern])))
        bd_delta = pd.tseries.offsets.BusinessDay(business_days_delta)
        most_recent_business_day = ((date_df - bd_delta).
                                                        timestamp.dt.strftime('%Y-%m-%d')[0])
        return most_recent_business_day
    
# The code blocks below can be deleted?
    def get_quarter_closing_date(self, date_in_report:str):
        """
        Find a company stock's last trading date in each quarter, by substracting by 
        2 days the quarter-ending date in the company's 10-Q SEC filings.
        """
        if not self.is_trading_day(date_in_report):
            closing_date = self.get_most_recent_busines_day_eastern(date_in_report)
        else:
            closing_date = date_in_report
        return closing_date

    def is_trading_day(self, input_date:str):
        nyse_trading_days = self.get_nyse_trading_days()
        input_date = pd.to_datetime(pd.Series([input_date]),format= '%Y-%m-%d')
        true_or_false = sum(nyse_trading_days.isin(input_date))
        return true_or_false == 1   

    def get_nyse_trading_days(self):
        today_in_datetime = datetime.today().date()
        today_in_string = datetime.strftime(today_in_datetime, '%Y-%m-%d')
        nyse = mcal.get_calendar('NYSE')
        nyse_trading_days = nyse.valid_days(start_date='2019-09-01', end_date= today_in_string)
        return nyse_trading_days   