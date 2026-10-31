class QuarterlyReport:
    __table__ = 'quarterly_reports'
    columns = ['id', 'date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'year', 'quarter']

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if hasattr(self, 'date') and hasattr(self.date, 'year'):
            self.year = self.date.year
            self.quarter = (self.date.month - 1) // 3 + 1
