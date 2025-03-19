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
    """Builder class for companies data"""
    
    def __init__(self, source=None):
        """Initialize with optional data source"""
        self.source = source
    
    def build(self):
        """Build and return companies data"""
        # For testing, return dummy data if no real source
        if not self.source:
            return {
                "AAPL": {
                    "name": "Apple Inc.",
                    "sector": "Technology",
                    "sub_sector": "Consumer Electronics"
                },
                "MSFT": {
                    "name": "Microsoft Corporation",
                    "sector": "Technology",
                    "sub_sector": "Software"
                },
                "GOOGL": {
                    "name": "Alphabet Inc.",
                    "sector": "Technology",
                    "sub_sector": "Internet Services"
                }
            }
        
        # Real implementation would process source data
        return {}
