import os
import csv
import re
import pytest
from api.src.adapters.wiki_page_client import ingest_sp500_stocks_info

MOCK_WIKI_HTML = """
<html>
<body>
    <table class="wikitable">
        <tr><th>Symbol</th><th>Security</th><th>SEC filings</th><th>GICS Sector</th><th>GICS Sub-Industry</th></tr>
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
        <tr><th></th><th>Ticker</th><th>Employees</th></tr>
        <tr><td>1</td><td>MMM</td><td>95000</td></tr>
        <tr><td>2</td><td>MSFT</td><td>181000</td></tr>
        <tr><td>3</td><td>ZTS</td><td>12000</td></tr>
    </table>
</body>
</html>
"""


@pytest.fixture
def ingest_result(requests_mock, tmp_path, monkeypatch):
    """
    Mock HTTP, redirect output to tmp_path, run ingest.
    Returns (file_path, csv_rows) so tests can assert both the path
    (quarter stamp) and the file contents.

    WIKI_DATA_FILEPATH in etl_service is patched to match the tmp_path
    destination so the cache-guard does not skip the mocked HTTP call.
    """
    requests_mock.get(
        'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
        text=MOCK_WIKI_HTML,
    )
    requests_mock.get(
        'https://www.liberatedstocktrader.com/sp-500-companies-list-by-number-of-employees/',
        text=MOCK_EMPLOYEES_HTML,
    )
    monkeypatch.setenv('DATA_DIR', str(tmp_path))

    # Ensure etl_service re-derives the filepath under tmp_path rather than
    # using the module-level constant (which was evaluated at import time with
    # the real DATA_DIR).
    from etl_service.src.utils.quarter import current_calendar_quarter
    quarter = current_calendar_quarter()
    stamped_filename = f"sp500_stocks_wiki_info_{quarter}.csv"
    expected_path = str(tmp_path / "data" / stamped_filename)
    monkeypatch.setattr(
        "etl_service.src.adapters.wiki_page_client.WIKI_DATA_FILEPATH",
        expected_path,
    )

    file_path = ingest_sp500_stocks_info()
    with open(file_path, 'r') as f:
        rows = list(csv.reader(f))
    return file_path, rows


# ---------------------------------------------------------------------------
# Quarter-stamp tests
# ---------------------------------------------------------------------------

def test_output_path_contains_quarter_stamp(ingest_result):
    """Filename must carry a YYYY_QN calendar-quarter stamp."""
    file_path, _ = ingest_result
    assert re.search(r'\d{4}_Q[1-4]', os.path.basename(file_path)), (
        f"Expected YYYY_QN stamp in filename, got: {os.path.basename(file_path)}"
    )


def test_output_path_is_absolute(ingest_result):
    file_path, _ = ingest_result
    assert os.path.isabs(file_path)


# ---------------------------------------------------------------------------
# Content tests
# ---------------------------------------------------------------------------

def test_column_names(ingest_result):
    _, csv_rows = ingest_result
    header = csv_rows[0]
    assert 'Ticker' in header
    assert 'Security' in header
    assert 'GICS Sector' in header
    assert 'GICS Sub-Industry' in header


def test_first_company_info(ingest_result):
    _, csv_rows = ingest_result
    header = csv_rows[0]
    ticker_idx = header.index('Ticker')
    security_idx = header.index('Security')
    sector_idx = header.index('GICS Sector')
    sub_idx = header.index('GICS Sub-Industry')
    first = csv_rows[1]
    assert first[ticker_idx] == 'MMM'
    assert first[security_idx] == '3M Company'
    assert first[sector_idx] == 'Industrials'
    assert first[sub_idx] == 'Industrial Conglomerates'


def test_last_company_info(ingest_result):
    _, csv_rows = ingest_result
    header = csv_rows[0]
    ticker_idx = header.index('Ticker')
    security_idx = header.index('Security')
    sector_idx = header.index('GICS Sector')
    sub_idx = header.index('GICS Sub-Industry')
    last = csv_rows[-1]
    assert last[ticker_idx] == 'ZTS'
    assert last[security_idx] == 'Zoetis'
    assert last[sector_idx] == 'Health Care'
    assert last[sub_idx] == 'Pharmaceuticals'
