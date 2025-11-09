import pytest
import csv
from api.src.adapters.wiki_page_client import ingest_sp500_stocks_info
import requests_mock

# Mock data for Wikipedia and Liberated Stock Trader
MOCK_WIKI_HTML = """
<html>
<body>
    <table class="wikitable">
        <tr><th>Ticker</th><th>Security</th><th>SEC filings</th><th>GICS Sector</th><th>GICS Sub-Industry</th></tr>
        <tr><td>MMM</td><td>3M Company</td><td>reports</td><td>Industrials</td><td>Industrial Conglomerates</td></tr>
        <tr><td>MSFT</td><td>Microsoft Corp</td><td>reports</td><td>Information Technology</td><td>Software</td></tr>
        <tr><td>ZTS</td><td>Zoetis</td><td>reports</td><td>Health Care</td><td>Pharmaceuticals</td></tr>
    </table>
</body>
</html>
"""

MOCK_EMPLOYEES_HTML = """
<html>
<body>
    <table>
        <tr><td></td><td>Ticker</td><td>Employees</td></tr>
        <tr><td>1</td><td>MMM</td><td>95000</td></tr>
        <tr><td>2</td><td>MSFT</td><td>181000</td></tr>
        <tr><td>3</td><td>ZTS</td><td>12000</td></tr>
    </table>
</body>
</html>
"""

@pytest.fixture
def mock_wiki_requests(requests_mock):
    requests_mock.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', text=MOCK_WIKI_HTML)
    requests_mock.get('https://www.liberatedstocktrader.com/sp-500-companies-list-by-number-of-employees/', text=MOCK_EMPLOYEES_HTML)

def read_csv_file(mock_wiki_requests): # Add mock_wiki_requests as a parameter
    import os
    # Remove existing file to force regeneration with mock data
    file_path = "./api/data/sp500/raw_data/sp500_stocks_wiki_info.csv"
    if os.path.exists(file_path):
        os.remove(file_path)
    file_path = ingest_sp500_stocks_info()
    with open(file_path, 'r') as f:
        csv_reader = csv.reader(f)
        return list(csv_reader)

def test_column_names(mock_wiki_requests): # Add mock_wiki_requests as a parameter
    csv_rows = read_csv_file(mock_wiki_requests)
    first_row = csv_rows[0]
    assert first_row[1:6] == ['Ticker', 'Security', 'SEC filings', 'GICS Sector', 'GICS Sub-Industry'] 

def test_first_company_info(mock_wiki_requests): # Add mock_wiki_requests as a parameter
    csv_rows = read_csv_file(mock_wiki_requests)
    second_row = csv_rows[1]
    assert second_row[1:6] == ['MMM', '3M Company', 'reports', 'Industrials', 'Industrial Conglomerates']

def test_last_company_info(mock_wiki_requests): # Add mock_wiki_requests as a parameter
    csv_rows = read_csv_file(mock_wiki_requests)
    last_row = csv_rows[-1]
    assert last_row[1:6] == ['ZTS', 'Zoetis', 'reports', 'Health Care', 'Pharmaceuticals']