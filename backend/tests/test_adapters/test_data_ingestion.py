import pytest
from api.src.adapters.data_ingestion_adapters import SECFilingAdapter, AlternativeDataAdapter

def test_sec_filing_adapter():
    adapter = SECFilingAdapter()
    raw_data = {
        'cik': '0000320193',
        'fiscalQuarter': 1,
        'fiscalYear': 2024,
        'revenues': 1000000,
        'operatingCosts': 800000,
        'netIncome': 200000
    }
    
    result = adapter.adapt(raw_data)
    assert result['company_id'] == '0000320193'
    assert result['revenue'] == 1000000
    assert result['net_income'] == 200000

def test_alternative_data_adapter():
    adapter = AlternativeDataAdapter()
    # Add alternative data adapter tests
