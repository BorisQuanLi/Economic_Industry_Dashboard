import json

def test_sector_avg_financial_performance(client):
    response = client.get('/sectors/?financial_indicator=revenue')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, dict)
    assert len(data) > 0