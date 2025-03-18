"""Financial metrics calculator for ETL process."""

class FinancialMetrics:
    """Calculate financial metrics from raw data"""
    
    def __init__(self):
        """Initialize financial metrics calculator"""
        pass
        
    def calculate_growth_rate(self, initial_value, final_value, periods=1):
        """Calculate compound annual growth rate"""
        if initial_value <= 0:
            return 0
        try:
            return (final_value / initial_value) ** (1 / periods) - 1
        except ZeroDivisionError:
            return 0
            
    def calculate_margin(self, revenue, profit):
        """Calculate profit margin"""
        if revenue == 0:
            return 0
        return profit / revenue
