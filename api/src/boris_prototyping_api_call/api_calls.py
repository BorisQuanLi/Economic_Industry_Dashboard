import datetime
from config import api_client

class ApiCalls:
    def __init__(self):
        pass

    def most_recent_busines_day(self, today = datetime.datetime.today().date()):
        offset = max(1, (today.weekday() + 6) % 7 - 3)  # Equation to find time elapsed
        timedelta = datetime.timedelta(offset)
        most_recent = today - timedelta
        return most_recent

    def most_recent_day_stock_info(self, stock_ticker):
        """
        stock_ticker: -> a stock's ticker in string, wrapped in quotation marks.
        
        Returns a tuple of two dictionaries from an Intrinio API call: 
            security_info and price_info
            
        From the security_info dictionary, a stock's ticker, company name can be 
        obtained with keys "ticker" and "name", respectively.
        
        From the price_info dictionary, "date" and "close" (closing price)
        can be obtained.  
        
        https://docs.intrinio.com/documentation/python
        """
        identifier = stock_ticker
        start_date = ''
        end_date = self.most_recent_busines_day()
        frequency = 'daily'
        page_size = 1
        next_page = ''
        response = (api_client.SecurityApi().
                                        get_security_stock_prices(identifier,
                                                                    start_date=start_date, 
                                                                    end_date=end_date, 
                                                                    frequency=frequency, 
                                                                    page_size=page_size, 
                                                                    next_page=next_page))
        security_info = response.security
        price_info = response.stock_prices[0]
        return security_info, price_info


    def get_historical_price(self, stock_ticker):
        """
        stock_ticker: -> a stock's ticker in string, wrapped in quotation marks.
        
        Returns a list of dictionaries from an Intrinio API call.
        Each dictionary consists of 'date' and 'value' (closing stock price.)
        
        The frequency of the historical data is set to quarterly.
        """
        identifier = stock_ticker
        tag = 'close_price'
        frequency = 'quarterly'
        type = ''
        start_date = ''
        end_date = self.most_recent_busines_day()
        sort_order = 'desc'
        page_size = 5
        next_page = ''

        response = (api_client.HistoricalDataApi().
                                            get_historical_data(identifier, 
                                                                tag, 
                                                                frequency=frequency, 
                                                                type=type, 
                                                                start_date=start_date, 
                                                                end_date=end_date, 
                                                                sort_order=sort_order, 
                                                                page_size=page_size, 
                                                                next_page=next_page))
        most_recent_business_day = response.historical_data[0]
        last_quarter_end = response.historical_data[1]
        last_year_end = response.historical_data[-1]
        return most_recent_business_day, last_quarter_end, last_year_end

"""
# check the functions in this module
api_call_client = ApiCalls()
print("Check the two ApiCalls methods based on the class definition in this module:")
print('_' * 15, '\n')

print("IBM's stock price info avalable from the data source in the most recent date: \n")
print(api_call_client.most_recent_day_stock_info('IBM'))
print('_' * 15, '\n')

print("Merck's historical stock prices: \n")
print(api_call_client.get_historical_price('MRK'))
"""