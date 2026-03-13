import json

def test_search_companies_success(client):
    """Test successful search for companies with valid parameters."""
    response = client.get('/companies/search?sub_sector_name=Application%20Software&financial_indicator=revenue')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0

def test_search_companies_invalid_indicator(client):
    """Test search for companies with an invalid financial indicator."""
    response = client.get('/companies/search?sub_sector_name=Application%20Software&financial_indicator=invalid_indicator')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == {'message': 'Please enter the name of a financial indicator.'}

def test_search_companies_all_sub_sectors(client):
    """Test search for all sub-sectors within a given sector."""
    response = client.get('/companies/search?sub_sector_name=all_sub_sectors&financial_indicator=Information%20Technology')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'sub_sector_names' in data
    assert isinstance(data['sub_sector_names'], list)

def test_company_financial_performance_success(client):
    """Test successful retrieval of company financial performance."""
    response = client.get('/sub_sectors/Application%20Software/companies?financial_indicator=revenue')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0

def test_company_financial_performance_invalid_indicator(client):
    """Test retrieval of company financial performance with an invalid indicator."""
    response = client.get('/sub_sectors/Application%20Software/companies?financial_indicator=invalid_indicator')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == {'message': 'Please enter the name of a financial indicator.'}