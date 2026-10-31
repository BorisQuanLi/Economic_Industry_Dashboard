class PricePE:
    __table__ = 'prices_pe'
    columns = ['id', 'date', 'company_id', 'closing_price', 'price_earnings_ratio', 'year', 'quarter']

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if hasattr(self, 'date') and hasattr(self.date, 'year'):
            self.year = self.date.year
            self.quarter = (self.date.month - 1) // 3 + 1
