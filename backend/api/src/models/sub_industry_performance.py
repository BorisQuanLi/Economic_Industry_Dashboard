from api.src.db import db
import api.src.models as models
from functools import reduce
from datetime import datetime

class SubIndustryPerformance:
    __table__ = "financial_numbers"
    columns = ['date', 'sub_industry_name', 'avg_closing_price', 'avg_pe_ratio', 'avg_revenue', 'avg_cost', 'avg_net_income']

    def __init__(self, **kwargs):
        """
        params: value of the 'date' attribute needs to be included.
        """
        for key in kwargs.keys():
            if key not in self.columns:
                raise f"{key} not in columns {self.columns}"
        for k, v in kwargs:
            setattr(self, k, v)

    