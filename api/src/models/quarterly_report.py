from api.src.db import db
from api.src import models

class QuarterlyReport:
    __table__ = 'quarterly_reports'
    columns = ['id', 'date', 'company_id', 'revenue', 'cost', 'net_income', 'earnings_per_share']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f'{key} not in {self.columns}'
        for k,v in kwargs.items():
            setattr(self, k, v)

    def find_revenue_by_company_id(self):
        pass

    def find_net_income_by_company_i(self, company_id, cursor):
        pass