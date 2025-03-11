import pytest
import csv
from api.src.adapters.wiki_page_client import ingest_sp500_stocks_info

def read_csv_file():
    file_path = './backend/api/data/sp500/raw_data/sp500_stocks_wiki_info.csv'
    with open(file_path, 'r') as f:
        csv_reader = csv.reader(f)
        return list(csv_reader)

def test_column_names():
    csv_rows = read_csv_file()
    first_row = csv_rows[0]
    assert first_row[1:6] == ['Ticker', 'Security', 'SEC filings', 'GICS Sector', 'GICS Sub-Industry'] 

def test_first_company_info():
    csv_rows = read_csv_file()
    second_row = csv_rows[1]
    assert second_row[1:6] == ['MMM', '3M Company', 'reports', 'Industrials', 'Industrial Conglomerates']

def test_last_company_info():
    csv_rows = read_csv_file()
    last_row = csv_rows[-1]
    assert last_row[1:6] == ['ZTS', 'Zoetis', 'reports', 'Health Care', 'Pharmaceuticals']