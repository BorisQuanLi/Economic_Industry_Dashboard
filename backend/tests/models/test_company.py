import pytest
from api.src.models.company import Company
from tests.helpers.build_records import build_records

def test_root_url(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {'message': 'API is running.'}