# Fix invalid import syntax
from etl.load.builders.database import DatabaseBuilder
# Fix the invalid syntax in the import statement
# from .financial_metrics import ... # New import statement
from .financial_metrics import FinancialMetrics  # Proper import

"""Financial data builder for ETL load process."""

class FinancialDataBuilder:
    """Builds financial data for analysis"""
    
    def __init__(self):
        pass
    
    def build_financial_data(self, data):
        """Build financial data"""
        return data
