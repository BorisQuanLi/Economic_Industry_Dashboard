import pytest
import pandas as pd
from backend.api.adapters.wiki_page_client import WikiPageClient

@pytest.fixture
def wiki_client():
    return WikiPageClient()

def test_get_sp500_wiki_data(wiki_client):
    df = wiki_client.get_sp500_wiki_data()
    assert not df.empty
    assert len(df) > 0

def test_column_names():
    df = pd.read_csv('./backend/api/data/sp500/raw_data/sp500_stocks_wiki_info.csv')
    expected_columns = ['Ticker', 'Security', 'GICS Sector', 'GICS Sub-Industry']
    for col in expected_columns:
        assert col in df.columns

def test_first_company_info():
    df = pd.read_csv('./backend/api/data/sp500/raw_data/sp500_stocks_wiki_info.csv')
    first_row = df.iloc[0]
    assert first_row['Ticker'] == 'MMM'
    assert first_row['Security'] == '3M Company'

def test_last_company_info():
    df = pd.read_csv('./backend/api/data/sp500/raw_data/sp500_stocks_wiki_info.csv')
    last_row = df.iloc[-1]
    assert last_row['Ticker'] == 'ZTS'
    assert last_row['Security'] == 'Zoetis'