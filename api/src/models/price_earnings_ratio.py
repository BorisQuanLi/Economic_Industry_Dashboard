from api.src.db import db
from api.src import models

class PriceEarningsRatio:
    __table__ = "price_earnings_ratios"
    columns = ['id', 'company_id', 'date', 'price_earnings_ratio']

    def __init__(self, **kwargs):
        def pe_ratio(self, kwargs):
            sql_str = f"""SELECT prices.closing_price 
                                 / quarterly_reports.earnings_per_share
                        FROM prices JOIN quarterly_reports
                        ON prices.company_id = quarterly_reports.company_id
                        WHERE prices.date = %s"""
            db.cursor(sql_str, (self.date,))
            pe = db.cursor.fetchone()
            self.price_earnings_ratio = pe

        for key in kwargs.keys():
            if key not in self.columns:
                raise f"{key} not in {self.columns}"
        for k, v in kwargs.items():
            setattr(self, k, v)

     