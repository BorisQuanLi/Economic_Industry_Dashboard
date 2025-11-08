import json

def test_sub_industries_within_sector(client):
    response = client.get('/sub_sectors/search?sector_name=Information%20Technology&financial_indicator=revenue')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) > 0

def test_get_sub_sector_names_within_sector(client):
    response = client.get('/sectors/Information%20Technology/sub_sectors')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'sub_sector_names' in data
    assert len(data['sub_sector_names']) > 0
