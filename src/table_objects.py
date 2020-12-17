from api_calls import *

class HistoricalPrices:
    __table__ = 'historical_prices'
    attributes = ['id', 'portfolio_position_id', 'stock_ticker', 
                'most_recent_business_day_available', 'last_quarter_end', 'last_year_end']
    api_call_client = ApiCalls()

    def __init__(self, stock_ticker):
        self.ticker = stock_ticker

    def historical_prices(self):
        most_recent_business_day_available, last_quarter_end, last_year_end = (
                self.api_call_client.get_historical_price(self.ticker))
        most_recent_price = most_recent_business_day_available.value
        last_quarter_price = last_quarter_end.value
        last_year_price = last_year_end.value
        # setattr() and/or build_from_record()?
        return most_recent_price, last_quarter_price, last_year_price

print("Check the historical_prices method works, based on the class definition in this module:")
print('_' * 15, '\n')

ibm = HistoricalPrices('IBM')
for price in ibm.historical_prices():
    print(price)

