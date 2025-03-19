"""Quarterly aggregation models for financial and price metrics."""
from etl.transform import models
from etl.transform.models.analytics.price_pe import PriceEarningsRatio
from etl.transform.models.analytics.quarterly import Quarterly

class QuarterlyPricePE(Quarterly):
    """Quarterly price and PE ratio data aggregation."""
    attributes = ['year', 'quarter', 'closing_price', 'price_earnings_ratio']
    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.attributes:
                print(f'{key} is not in class attributes {self.attibutes}.')
        for key, value in kwargs.items():
            setattr(self, key, value)

class QuarterlyReportResult:
    """Quarterly financial report result data structure."""
    attributes = ['year', 'quarter', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin']
    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.attributes:
                print(f'{key} is not in class attributes {self.attributes}.')
        for key, value in kwargs.items():
            setattr(self, key, value)

class QuarterlyFinancials(Quarterly):
    """Quarterly financial data aggregation."""
    pass

__all__ = ['QuarterlyFinancials']