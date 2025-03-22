import pytest
from unittest.mock import MagicMock

# Update imports to match actual class names
from backend.etl.extract.wiki_client import WikiPageClient
from backend.etl.extract.companies_extractor import CompaniesExtractor, CompaniesBuilder  # Updated import

# Remove the non-existent WikiExtractor class import
# from backend.etl.extract.wiki_client import WikiExtractor

def test_wiki_page_client():
    """Test wiki page client functionality"""
    client = WikiPageClient()
    # Add your test assertions here
    assert client is not None

def test_companies_extractor():
    extractor = CompaniesExtractor()
    companies = extractor.extract()
    assert companies is not None
    assert len(companies) > 0

def test_companies_builder():
    builder = CompaniesBuilder()
    companies = builder.build()
    assert companies is not None
    assert len(companies) > 0
