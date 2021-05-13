class QuarterlyPricePE:
    attributes = ['year', 'quarter', 'closing_price', 'price_earnings_ratio']
    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.attributes:
                print(f'{key} is not in class attributes {self.attibutes}.')
                # return?
        for key, value in kwargs.items():
            setattr(self, key, value)


class QuarterlyReportResult:
    attibutes = ['year', 'quarter', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin']
    pass