"""Analytics models for the application."""

# Export key classes
from .aggregation_by_quarter import QuarterlyPricePE, QuarterlyReportResult, QuarterlyFinancials
from .price_pe import PriceEarningsRatio
# Placeholder for FinancialMetrics if it doesn't exist yet
class FinancialMetrics:
    """Financial metrics calculations."""
    pass

__all__ = [
    'QuarterlyPricePE', 
    'QuarterlyReportResult', 
    'QuarterlyFinancials',
    'PriceEarningsRatio',
    'FinancialMetrics'
]
