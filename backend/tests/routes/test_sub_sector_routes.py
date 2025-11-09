import json

def test_sub_industries_within_sector_success(client):
    """Test successful search for sub-industries within a sector."""
    response = client.get('/sub_sectors/search?sector_name=Information%20Technology&financial_indicator=revenue')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0

def test_sub_industries_within_sector_invalid_indicator(client):
    """Test search for sub-industries with an invalid financial indicator."""
    response = client.get('/sub_sectors/search?sector_name=Information%20Technology&financial_indicator=invalid_indicator')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == {'message': 'Please enter the name of a financial indicator.'}

def test_sub_industries_within_sector_all_sectors(client):
    """Test search for all sector names."""
    response = client.get('/sub_sectors/search?sector_name=all_sectors')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'all_sector_names' in data
    assert isinstance(data['all_sector_names'], list)

def test_get_sub_sector_names_within_sector_success(client):
    """Test successful retrieval of sub-sector names within a sector."""
    response = client.get('/sectors/Information%20Technology/sub_sectors')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'sub_sector_names' in data
    assert len(data['sub_sector_names']) > 0