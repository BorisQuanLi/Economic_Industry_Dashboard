from urllib.request import urlopen
import json
from datetime import datetime, timedelta
import pytz
import pandas as pd
import api.src.models as models
import api.src.db as db
from settings import API_KEY

class QuarterFinancialsPricePEBuilder:
    financials_attributes = ['date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin'] 
    prices_pe_attributes = ['date', 'company_id', 'closing_price', 'price_earnings_ratio']

    def __init__(self, ticker, conn, cursor):
        self.conn = conn
        self.cursor = cursor
        self.ticker = ticker
        self.recent_five_quarterly_report_records = self.get_quarterly_financials(ticker)
        self.historical_prices_dict = self.get_stock_daily_prices(ticker)

    def get_quarterly_financials(self, ticker):
        response = urlopen(f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?period=quarter&apikey={API_KEY}")
        data = response.read().decode("utf8")
        qtr_ic = json.loads(data)
        recent_five_quarterly_report_records = qtr_ic[:5]
        # skip record with an invalid revenue value of 0
        recent_five_quarterly_report_records = [quarterly_record for quarterly_record in recent_five_quarterly_report_records
                                                                            if int(quarterly_record['revenue']) != 0]
        return recent_five_quarterly_report_records


    def get_stock_daily_prices(self, ticker:str, number_days=500):
        response = urlopen(f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?serietype=line&apikey={API_KEY}")
        data = response.read().decode("utf8")
        all_historical_prices = json.loads(data)['historical']
        # get only the needed number of days of closing prices
        daily_historical_prices =  all_historical_prices[:number_days]
        historical_prices_dict = {day['date']: day['close']
                                                        for day in daily_historical_prices}
        return historical_prices_dict

    def run(self, company_id, sector_name):       
        self.find_or_save_quarterly_financials_records(company_id)
        self.find_or_save_price_pe_records(company_id)

    def find_or_save_quarterly_financials_records(self, company_id):
        if not db.find(models.QuarterlyReport, company_id, self.cursor):
            for quarterly_record in self.recent_five_quarterly_report_records:
                self.find_or_save_quarterly_record(company_id, quarterly_record)             

    def find_or_save_quarterly_record(self, company_id, quarterly_record):
        values_vector = self.get_financials_vector(quarterly_record, company_id)
        quarter_report_dict = dict(zip(self.financials_attributes, values_vector))
        obj = models.QuarterlyReport(**quarter_report_dict)
        db.save(obj, self.conn, self.cursor)
        
    def get_financials_vector(self, quarterly_record, company_id):
        profit_margin = round(100 * quarterly_record['netIncome']
                                / quarterly_record['revenue'], 2)
        values_vector = [quarterly_record['date'],
                         company_id,
                         quarterly_record['revenue'],
                         quarterly_record['netIncome'],
                         round(quarterly_record['eps'], 2),
                         profit_margin]
        return values_vector

    def find_or_save_price_pe_records(self, company_id):
        if not db.find(models.PricePE, company_id, self.cursor):
            for quarterly_info_row in self.recent_five_quarterly_report_records:
                values_vector = self.get_price_pe_values_vector(company_id, quarterly_info_row)
                price_de_dict = dict(zip(self.prices_pe_attributes, values_vector))
                obj = models.PricePE(**price_de_dict)
                price_pe_obj = db.save(obj, self.conn, self.cursor)

    def get_price_pe_values_vector(self, company_id, quarterly_info_row):
        date, closing_price = self.get_quarter_closing_date_price(quarterly_info_row['date'])
        eps = quarterly_info_row['eps']
        p_e_ratio = closing_price / eps
        values_vector = [date, company_id, closing_price, p_e_ratio]
        return values_vector

    def get_quarter_closing_date_price(self, date_in_report:str):
        found_most_recent_trading_day = False
        while not found_most_recent_trading_day:
            try:
                most_recent_trading_day = self.get_most_recent_busines_day_eastern(date_in_report)
                closing_price = round(self.historical_prices_dict[most_recent_trading_day], 2)
                found_most_recent_trading_day = True
            except:
                # move the date earlier by one business day
                print(date_in_report)
                date_in_report = self.get_most_recent_busines_day_eastern(date_in_report)
                continue
        return most_recent_trading_day, closing_price

    def get_most_recent_busines_day_eastern(self, date:str, business_days_delta=1):
        date_eastern = self.get_date_eastern(date)
        date_df = pd.DataFrame(dict(
                                    timestamp=pd.to_datetime([date_eastern])))
        bd_delta = pd.tseries.offsets.BusinessDay(business_days_delta)
        most_recent_business_day_eastern = ((date_df - bd_delta).
                                                        timestamp.dt.strftime('%Y-%m-%d')[0])                                           
        return most_recent_business_day_eastern
    
    def get_date_eastern(self, date:str):
        if len(date.split('-')) > 1:
            date_in_datetime = datetime.strptime(date, "%Y-%m-%d")
        else:
            date_in_datetime = datetime.strptime(date, "%Y%m%d")
        date_eastern = date_in_datetime.astimezone(
                                                pytz.timezone('US/Eastern')).date()
        date_eastern_str = datetime.strftime(date_eastern, '%Y-%m-%d')
        return date_eastern_str

