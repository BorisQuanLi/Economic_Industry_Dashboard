"""
Database Query Service

This module handles complex database queries for the application.
"""

import logging
from typing import List, Dict, Any, Optional
from .base_service import BaseDatabaseService

logger = logging.getLogger(__name__)

class QueryService(BaseDatabaseService):
    """Service for executing domain-specific database queries."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    # Sector and sub-industry quarterly financial queries
    
    def get_sector_quarterly_financials(self, sector_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get quarterly financial data for a sector."""
        # Import here to avoid circular imports
        from backend.etl.load.db.queries.sql_query_strings import SECTOR_QUARTERLY_FINANCIALS
        
        sql_str = SECTOR_QUARTERLY_FINANCIALS
        return self.fetch_records(sql_str, (sector_name, limit))
    
    def get_sub_sector_quarterly_financials(self, sub_sector_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get quarterly financial data for a sub-sector."""
        # Import here to avoid circular imports
        from backend.etl.load.db.queries.sql_query_strings import SUB_SECTOR_QUARTERLY_FINANCIALS
        
        sql_str = SUB_SECTOR_QUARTERLY_FINANCIALS
        return self.fetch_records(sql_str, (sub_sector_name, limit))
    
    # Price and P/E ratio queries
    
    def get_sector_price_pe(self, sector_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get price and P/E ratio data for a sector."""
        # Import here to avoid circular imports
        from backend.etl.load.db.queries.sql_query_strings import SECTOR_PRICE_PE
        
        sql_str = SECTOR_PRICE_PE
        return self.fetch_records(sql_str, (sector_name, limit))
    
    def get_sub_sector_price_pe(self, sub_sector_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get price and P/E ratio data for a sub-sector."""
        # Import here to avoid circular imports
        from backend.etl.load.db.queries.sql_query_strings import SUB_SECTOR_PRICE_PE
        
        sql_str = SUB_SECTOR_PRICE_PE
        return self.fetch_records(sql_str, (sub_sector_name, limit))
    
    # Company specific queries
    
    def get_company_financials(self, ticker: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get financial data for a specific company by ticker."""
        # Import here to avoid circular imports
        from backend.etl.load.db.queries.sql_query_strings import COMPANY_FINANCIALS
        
        sql_str = COMPANY_FINANCIALS
        return self.fetch_records(sql_str, (ticker, limit))
    
    def get_company_price_history(self, ticker: str, start_date: str = None, end_date: str = None, 
                                 limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical price data for a specific company."""
        # Import here to avoid circular imports
        from backend.etl.load.db.queries.sql_query_strings import COMPANY_PRICE_HISTORY
        
        params = [ticker]
        query_parts = []
        
        if start_date:
            query_parts.append("date >= %s")
            params.append(start_date)
        
        if end_date:
            query_parts.append("date <= %s")
            params.append(end_date)
            
        params.append(limit)
        
        sql_str = COMPANY_PRICE_HISTORY.format(
            where_clause=f"AND {' AND '.join(query_parts)}" if query_parts else ""
        )
        
        return self.fetch_records(sql_str, tuple(params))
    
    # Economic indicator queries
    
    def get_economic_indicators(self, indicator_type: str = None, 
                              start_date: str = None, end_date: str = None,
                              limit: int = 50) -> List[Dict[str, Any]]:
        """Get economic indicator data with optional filtering."""
        # Import here to avoid circular imports
        from backend.etl.load.db.queries.sql_query_strings import ECONOMIC_INDICATORS
        
        params = []
        where_clauses = []
        
        if indicator_type:
            where_clauses.append("indicator_type = %s")
            params.append(indicator_type)
            
        if start_date:
            where_clauses.append("date >= %s")
            params.append(start_date)
            
        if end_date:
            where_clauses.append("date <= %s")
            params.append(end_date)
            
        params.append(limit)
        
        where_clause = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        sql_str = ECONOMIC_INDICATORS.format(where_clause=where_clause)
        
        return self.fetch_records(sql_str, tuple(params))
    
    def get_gdp_growth(self, quarters: int = 20) -> List[Dict[str, Any]]:
        """Get GDP growth data for the most recent quarters."""
        # Import here to avoid circular imports
        from backend.etl.load.db.queries.sql_query_strings import GDP_GROWTH
        
        sql_str = GDP_GROWTH
        return self.fetch_records(sql_str, (quarters,))
    
    def get_unemployment_rate(self, months: int = 36) -> List[Dict[str, Any]]:
        """Get unemployment rate data for the most recent months."""
        # Import here to avoid circular imports
        from backend.etl.load.db.queries.sql_query_strings import UNEMPLOYMENT_RATE
        
        sql_str = UNEMPLOYMENT_RATE
        return self.fetch_records(sql_str, (months,))
    
    # Custom queries
    
    def execute_custom_query(self, query: str, params=None) -> List[Dict[str, Any]]:
        """
        Execute a custom query with parameters.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of result dictionaries
        """
        return self.fetch_records(query, params)
    
    def get_metrics_by_date_range(self, table: str, start_date: str, end_date: str, 
                                group_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get metrics from a table within a date range.
        
        Args:
            table: Table name
            start_date: Start date string (YYYY-MM-DD)
            end_date: End date string (YYYY-MM-DD)
            group_by: Optional column to group by
            
        Returns:
            List of metrics
        """
        group_clause = f"GROUP BY {group_by}" if group_by else ""
        
        query = f"""
            SELECT * FROM {table}
            WHERE date BETWEEN %s AND %s
            {group_clause}
            ORDER BY date
        """
        
        return self.fetch_records(query, (start_date, end_date))
    
    # Data comparison and correlation queries
    
    def get_sector_comparison(self, sectors: List[str], metric: str, 
                             start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Compare a specific metric across multiple sectors.
        
        Args:
            sectors: List of sector names
            metric: Financial metric to compare
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Comparison data
        """
        # Import here to avoid circular imports
        from backend.etl.load.db.queries.sql_query_strings import SECTOR_COMPARISON
        
        params = []
        where_clauses = []
        
        # Add sectors to parameters
        params.extend(sectors)
        
        if start_date:
            where_clauses.append("date >= %s")
            params.append(start_date)
            
        if end_date:
            where_clauses.append("date <= %s")
            params.append(end_date)
        
        where_clause = f"AND {' AND '.join(where_clauses)}" if where_clauses else ""
        sql_str = SECTOR_COMPARISON.format(
            metric=metric,
            num_sectors=len(sectors),
            where_clause=where_clause
        )
        
        return self.fetch_records(sql_str, tuple(params))
    
    def get_metric_correlation(self, metric1: str, metric2: str, entity_type: str, 
                             entity_name: str = None, period: int = 36) -> Dict[str, Any]:
        """
        Calculate correlation between two metrics.
        
        Args:
            metric1: First metric name
            metric2: Second metric name
            entity_type: 'sector', 'sub_sector', or 'company'
            entity_name: Name of sector, sub-sector, or company ticker
            period: Number of periods to analyze
            
        Returns:
            Correlation statistics
        """
        # Import here to avoid circular imports
        from backend.etl.load.db.queries.sql_query_strings import METRIC_CORRELATION
        
        params = [metric1, metric2, period]
        entity_clause = ""
        
        if entity_name:
            if entity_type == 'sector':
                entity_clause = "AND sector_name = %s"
            elif entity_type == 'sub_sector':
                entity_clause = "AND sub_sector_name = %s"
            elif entity_type == 'company':
                entity_clause = "AND ticker = %s"
            
            params.append(entity_name)
        
        sql_str = METRIC_CORRELATION.format(
            entity_clause=entity_clause,
            entity_type=entity_type
        )
        
        results = self.fetch_records(sql_str, tuple(params))
        return results[0] if results else {"correlation": None}
