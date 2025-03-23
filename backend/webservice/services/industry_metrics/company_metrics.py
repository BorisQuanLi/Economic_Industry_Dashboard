"""
Company Metrics Service

This module serves as the main entry point for company-related metrics and analysis,
coordinating between specialized company data services.
"""

import logging
from typing import List, Optional, Dict, Any
from ..database.base_service import BaseDatabaseService
from backend.etl.transform.models.company.company_info_model import CompanyInfo
from .company_data.company_info_service import CompanyInfoService
from .company_data.company_financial_service import CompanyFinancialService
from .company_data.company_price_service import CompanyPriceService
from .company_data.company_comparison_service import CompanyComparisonService

logger = logging.getLogger(__name__)

class CompanyService(BaseDatabaseService):
    """Service that coordinates company-related database operations and analysis."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize specialized services
        self.info_service = CompanyInfoService(self.repo)
        self.financial_service = CompanyFinancialService(self.repo)
        self.price_service = CompanyPriceService(self.repo)
        self.comparison_service = CompanyComparisonService(self.repo)
    
    # Company information methods
    def find_company_by_ticker(self, ticker_symbol: str) -> Optional[CompanyInfo]:
        """Find a company by its ticker symbol."""
        return self.info_service.find_by_ticker(ticker_symbol)
    
    def find_companies_by_sector(self, sector_name: str) -> List[CompanyInfo]:
        """Find all companies in a specific sector."""
        return self.info_service.find_by_sector(sector_name)
        
    def find_companies_by_sub_industry(self, sub_industry_name: str) -> List[CompanyInfo]:
        """Find all companies in a specific sub-industry."""
        return self.info_service.find_by_sub_industry(sub_industry_name)
    
    # Company financials methods
    def get_company_financials(self, ticker: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get quarterly financial data for a specific company by ticker."""
        return self.financial_service.get_financials_by_ticker(ticker, limit)
    
    def get_company_financials_history(self, company_id: int, time_period: str = 'quarterly') -> Optional[Dict[str, Any]]:
        """Get historical financial data for a company."""
        return self.financial_service.get_financials_history(company_id, time_period)
    
    # Company price and PE ratio methods
    def get_company_pe_history(self, company_id: int, months: int = 12) -> Optional[Dict[str, Any]]:
        """Get historical P/E ratio data for a company."""
        return self.price_service.get_pe_history(company_id, months)
    
    # Company comparison methods
    def get_company_comparison(self, company_ids: List[int]) -> Dict[str, Any]:
        """Compare multiple companies across key financial metrics."""
        return self.comparison_service.compare_companies(company_ids)
    
    # Comprehensive company data methods
    def get_company_data(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed data for a specific company including basic info, financials, and P/E data."""
        # This method calls various services to build a comprehensive company profile
        company_info = self.info_service.find_by_id(company_id)
        if not company_info:
            return None
            
        # Gather data from different services
        latest_financials = self.financial_service.get_latest_financials(company_id)
        latest_pe = self.price_service.get_latest_pe(company_id)
        metrics = self.financial_service.get_growth_metrics(company_id)
        percentiles = {
            'revenue_percentile': self.financial_service.get_revenue_percentile(company_id),
            'pe_percentile': self.price_service.get_pe_percentile(company_id)
        }
        
        # Combine all data
        return {
            'company': company_info,
            'latest_financials': latest_financials,
            'latest_pe': latest_pe,
            'metrics': {**metrics, **percentiles}
        }
        
    # Methods from CompanyAnalysisService to be integrated
    def get_company_financials_analysis(self, company_id: int) -> Dict[str, Any]:
        """
        Get comprehensive financial analysis for a company.
        
        This method combines direct model access like CompanyAnalysisService with the 
        existing service architecture.
        
        Args:
            company_id: The ID of the company
            
        Returns:
            Dictionary containing financial analysis
        """
        quarterly_reports = CompanyQuarterlyReport.find_by_company_id(company_id, self.repo.cursor)
        price_earnings_data = PriceEarningsRatio.find_by_company_id(company_id, self.repo.cursor)
        
        return {
            'metrics': {
                'revenue_growth': CompanyQuarterlyReport.calculate_growth_rate(company_id, 'revenue', self.repo.cursor),
                'profit_margin': CompanyQuarterlyReport.get_metric_percentile(company_id, 'profit_margin', self.repo.cursor),
                'pe_ratio': PriceEarningsRatio.calculate_average_pe(company_id, self.repo.cursor),
                'pe_percentile': PriceEarningsRatio.get_pe_percentile(company_id, self.repo.cursor)
            },
            'quarterly_reports': quarterly_reports,
            'price_earnings_history': price_earnings_data
        }
        
    def get_quarterly_reports_by_ticker(self, ticker: str) -> List[Dict[str, Any]]:
        """
        Get quarterly reports for a company by ticker symbol.
        
        Args:
            ticker: The ticker symbol of the company
            
        Returns:
            List of quarterly reports
        """
        try:
            return CompanyQuarterlyReport.find_by_company_ticker(ticker, self.repo.cursor)
        except Exception as e:
            logger.error(f"Error getting quarterly reports by ticker: {str(e)}")
            return []
            
    def get_company_by_ticker(self, ticker: str) -> Optional[CompanyInfo]:
        """
        Get company information by ticker symbol.
        
        This is an alias for find_company_by_ticker to maintain compatibility
        with the CompanyAnalysisService interface.
        
        Args:
            ticker: The ticker symbol of the company
            
        Returns:
            CompanyInfo object or None if not found
        """
        return self.find_company_by_ticker(ticker)

class CompanyMetrics:
    """Service for company metrics calculations."""
    
    def __init__(self):
        """Initialize the company metrics service."""
        logger.info("CompanyMetrics initialized")
    
    def get_companies(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all companies with pagination.
        
        Args:
            limit: Maximum number of companies to return
            offset: Number of companies to skip
            
        Returns:
            List of company dictionaries
        """
        # Mock implementation - return sample companies
        companies = [
            {"id": 1, "ticker": "AAPL", "name": "Apple Inc.", "sector_id": 1},
            {"id": 2, "ticker": "MSFT", "name": "Microsoft Corp.", "sector_id": 1},
            {"id": 3, "ticker": "GOOGL", "name": "Alphabet Inc.", "sector_id": 1},
            {"id": 4, "ticker": "AMZN", "name": "Amazon.com Inc.", "sector_id": 1},
            {"id": 5, "ticker": "META", "name": "Meta Platforms Inc.", "sector_id": 1},
            {"id": 6, "ticker": "JNJ", "name": "Johnson & Johnson", "sector_id": 2},
            {"id": 7, "ticker": "PFE", "name": "Pfizer Inc.", "sector_id": 2},
            {"id": 8, "ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector_id": 3},
            {"id": 9, "ticker": "BAC", "name": "Bank of America Corp.", "sector_id": 3},
            {"id": 10, "ticker": "WMT", "name": "Walmart Inc.", "sector_id": 4},
        ]
        
        # Apply pagination
        paginated = companies[offset:offset + limit]
        return paginated
    
    def get_companies_by_sector(self, sector_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get companies by sector with pagination.
        
        Args:
            sector_id: Sector ID
            limit: Maximum number of companies to return
            offset: Number of companies to skip
            
        Returns:
            List of company dictionaries
        """
        # Get all companies first (in a real implementation, we'd filter at the database level)
        all_companies = self.get_companies()
        
        # Filter by sector ID
        sector_companies = [c for c in all_companies if c.get('sector_id') == sector_id]
        
        # Apply pagination
        paginated = sector_companies[offset:offset + limit]
        return paginated
    
    def get_company_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed data for a company.
        
        Args:
            ticker: Company ticker symbol
            
        Returns:
            Company data dictionary or None if not found
        """
        # Mock implementation - find company by ticker from sample data
        companies = {
            "AAPL": {
                "id": 1, 
                "ticker": "AAPL", 
                "name": "Apple Inc.", 
                "sector_id": 1,
                "description": "Technology company that designs and manufactures consumer electronics.",
                "website": "https://www.apple.com",
                "headquarters": "Cupertino, CA",
                "founded": 1976
            },
            "MSFT": {
                "id": 2, 
                "ticker": "MSFT", 
                "name": "Microsoft Corp.", 
                "sector_id": 1,
                "description": "Technology company that develops software and hardware.",
                "website": "https://www.microsoft.com",
                "headquarters": "Redmond, WA",
                "founded": 1975
            }
            # Add more companies as needed
        }
        
        return companies.get(ticker)
    
    def get_company_financials(self, ticker: str, 
                             time_period: str = 'quarterly',
                             metrics: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get financial metrics for a company.
        
        Args:
            ticker: Company ticker symbol
            time_period: Time period ('quarterly', 'annual')
            metrics: List of specific metrics to get (None for all)
            
        Returns:
            Financial data dictionary or None if company not found
        """
        # Get the company data first
        company = self.get_company_data(ticker)
        if not company:
            return None
            
        # Mock financial data
        financial_data = {
            "revenue": [
                {"date": "2023-12-31", "value": 123400000000},
                {"date": "2023-09-30", "value": 117100000000},
                {"date": "2023-06-30", "value": 111800000000},
                {"date": "2023-03-31", "value": 94800000000}
            ],
            "net_income": [
                {"date": "2023-12-31", "value": 34000000000},
                {"date": "2023-09-30", "value": 31500000000},
                {"date": "2023-06-30", "value": 29800000000},
                {"date": "2023-03-31", "value": 24160000000}
            ],
            "eps": [
                {"date": "2023-12-31", "value": 2.18},
                {"date": "2023-09-30", "value": 2.01},
                {"date": "2023-06-30", "value": 1.88},
                {"date": "2023-03-31", "value": 1.52}
            ]
        }
        
        # Filter metrics if specified
        if metrics:
            financial_data = {k: v for k, v in financial_data.items() if k in metrics}
            
        # Add company info
        result = {
            "company": company,
            "financials": financial_data,
            "time_period": time_period
        }
        
        return result
