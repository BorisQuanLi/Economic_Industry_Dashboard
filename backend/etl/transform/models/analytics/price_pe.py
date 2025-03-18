# from api.src.db import db # Old import
# from api.src import models # Old import

from etl.load.db import connection as db
from etl.transform import models

class PriceMetrics:
    __table__ = 'prices_pe' 
    columns = ['id', 'date', 'company_id', 'closing_price', 'price_earnings_ratio']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f"{key} not in {self.columns}"
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_company_id(self, company_id, cursor):
        sql_str = f"""SELECT * FROM {self.__table__}
                        WHERE company_id = %s;"""
        cursor.execute(sql_str, (company_id,))
        records = cursor.fetchall()
        return db.build_from_records(models.SubIndustry, records)

class PriceEarningsRatio:
    """Class to handle Price-to-Earnings ratio calculations and analysis."""
    
    def __init__(self, price=None, earnings=None):
        self.price = price
        self.earnings = earnings
        
    def calculate(self):
        """Calculate P/E ratio.
        
        Returns:
            float: P/E ratio or None if earnings are zero or None
        """
        if not self.earnings:
            return None
        try:
            return self.price / self.earnings if self.earnings != 0 else None
        except (TypeError, ZeroDivisionError):
            return None
            
    def is_valid(self):
        """Check if P/E ratio can be calculated with current data."""
        return self.price is not None and self.earnings is not None and self.earnings != 0