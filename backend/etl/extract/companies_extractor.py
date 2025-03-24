from typing import List, Dict, Any, Optional
import pandas as pd
import os
import re
from .wiki_client import WikipediaDataIngestionClient

class CompaniesExtractor:
    """Extracts S&P 500 companies data from source"""
    
    def __init__(self):
        self.wiki_client = WikipediaDataIngestionClient()
        
    def extract(self) -> pd.DataFrame:
        """Extract companies data from Wikipedia
        
        Returns:
            pd.DataFrame: DataFrame containing company data
            
        Raises:
            Exception: If data extraction fails
        """
        try:
            # Get the path to the CSV file (will trigger ingestion if needed)
            csv_filepath = self.wiki_client.ingest_sp500_company_info()
            
            # Read the CSV into a DataFrame
            df = pd.read_csv(csv_filepath)
            
            return df
        except Exception as e:
            raise Exception(f"Failed to extract companies data: {str(e)}")

class CompaniesBuilder:
    """Builder class for transforming raw companies data into structured model data"""
    
    def __init__(self, source_path: Optional[str] = None):
        """Initialize with optional path to source CSV file
        
        Args:
            source_path: Path to the CSV file containing raw company data
        """
        self.source_path = source_path
    
    def build(self) -> List[Dict[str, Any]]:
        """Build structured company data from raw source
        
        Returns:
            List[Dict[str, Any]]: List of company records with transformed attributes
        """
        # For testing when no source path is provided
        if not self.source_path:
            return self._get_dummy_data()
        
        # Read the CSV into a DataFrame
        df = pd.read_csv(self.source_path)
        
        # Transform the data to match required columns structure
        companies = []
        
        for index, row in df.iterrows():
            # Extract state from headquarters location using regex
            hq_state = None
            if 'Headquarters Location' in row:
                location = row['Headquarters Location']
                state_match = re.search(r',\s*([A-Za-z\s]+)$', location)
                if state_match:
                    hq_state = state_match.group(1).strip()
            
            # Extract year founded (handling cases like "1989 (1887)")
            year_founded = None
            if 'Founded' in row:
                founded = row['Founded']
                year_match = re.search(r'^(\d{4})', founded)
                if year_match:
                    year_founded = int(year_match.group(1))
            
            # Map sub-industry to sub_industry_id (you'll need a lookup)
            # This is a placeholder - you'd need actual mapping logic
            sub_industry_id = self._get_sub_industry_id(row.get('GICS Sub-Industry', ''))
            
            company = {
                'id': index + 1,  # Generate ID (or you could use another unique identifier)
                'name': row.get('Security', ''),
                'ticker': row.get('Symbol', ''),
                'sub_industry_id': sub_industry_id,
                'year_founded': year_founded,
                'number_of_employees': None,  # Not available in the raw data
                'HQ_state': hq_state
            }
            
            companies.append(company)
        
        return companies
    
    def _get_sub_industry_id(self, sub_industry_name: str) -> Optional[int]:
        """Map sub-industry name to ID (placeholder implementation)
        
        In a real implementation, this would query a database or use a mapping table
        to get the correct sub_industry_id for a given sub-industry name.
        """
        # Placeholder mapping logic - replace with actual implementation
        # This could query a database table of sub-industries
        sub_industry_mapping = {
            "Internet Services & Infrastructure": 101,
            "Semiconductors": 102,
            "Application Software": 103,
            # ... other mappings ...
        }
        
        return sub_industry_mapping.get(sub_industry_name)
    
    def _get_dummy_data(self) -> List[Dict[str, Any]]:
        """Return dummy data for testing when no source is available"""
        return [
            {
                "id": 1,
                "name": "Apple Inc.",
                "ticker": "AAPL",
                "sector": "Technology",
                "sub_industry_id": 101,
                "year_founded": 1977,
                "number_of_employees": 147000,
                "HQ_state": "California"
            },
            {
                "id": 2,
                "name": "Microsoft Corporation",
                "ticker": "MSFT",
                "sector": "Technology",
                "sub_industry_id": 103,
                "year_founded": 1975,
                "number_of_employees": 181000,
                "HQ_state": "Washington"
            },
            {
                "id": 3,
                "name": "Alphabet Inc.",
                "ticker": "GOOGL",
                "sector": "Technology",
                "sub_industry_id": 101,
                "year_founded": 1998,
                "number_of_employees": 156000,
                "HQ_state": "California"
            }
        ]
