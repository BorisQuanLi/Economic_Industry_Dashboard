import pytest
from flask import Flask

# Update import to use the webservice module instead of api
from backend.webservice.factory import create_app

def test_health_endpoint(client):
    """Test health endpoint returns 200"""
    response = client.get('/health')
    assert response.status_code == 200
