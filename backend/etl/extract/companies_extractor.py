from typing import List, Dict, Any
from .wiki_client import WikiPageClient

class CompaniesExtractor:
    """Extracts and processes S&P 500 companies data"""
    
    def __init__(self):
        self.wiki_client = WikiPageClient()
        
    def extract(self) -> List[Dict[str, Any]]:
        """Extract and process companies data from Wikipedia
        
        Returns:
            List[Dict[str, Any]]: List of company records
            
        Raises:
            Exception: If data extraction fails
        """
        try:
            sp500_data = self.wiki_client.extract_sp500_data()
            return sp500_data.to_dict('records')
        except Exception as e:
            raise Exception(f"Failed to extract companies data: {str(e)}")

class CompaniesBuilder:
    """Builder class for constructing company data objects"""
    
    def __init__(self, data=None):
        self.data = data or {}
        
    def with_ticker(self, ticker):
        """Add ticker symbol to the company data"""
        self.data['ticker'] = ticker
        return self
        
    def with_name(self, name):
        """Add company name to the company data"""
        self.data['name'] = name
        return self
        
    def with_sector(self, sector):
        """Add sector information to the company data"""
        self.data['sector'] = sector
        return self
        
    def with_industry(self, industry):
        """Add industry information to the company data"""
        self.data['industry'] = industry
        return self
    
    def with_financial_data(self, financial_data):
        """Add financial data to the company information"""
        self.data['financial_data'] = financial_data
        return self
    
    def build(self):
        """Return the constructed company data object"""
        return self.data
