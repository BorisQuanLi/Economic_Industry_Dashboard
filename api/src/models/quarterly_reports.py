
class QuarterlyReport:
    __table__ = 'quarterly_results'
    columns = ['id', 'date', 'company_id', 'net_income', 'price_earnings_ratio']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f'{key} not in {self.columns}'
        for k,v in kwargs.items():
            setattr(self, k, v)


"""
    def net_income, or price_earnings_ratio ()
change financials to quarterly_reports
change sectors to sub_sectors
"""    
    