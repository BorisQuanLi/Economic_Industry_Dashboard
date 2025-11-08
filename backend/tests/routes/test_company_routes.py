import json

def test_search_companies(client):
    response = client.get('/companies/search?sub_sector_name=Application%20Software&financial_indicator=revenue')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0

def test_company_financial_performance(client):
    response = client.get('/sub_sectors/Application%20Software/companies?financial_indicator=revenue')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0
