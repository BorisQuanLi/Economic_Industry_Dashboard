import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_sliding_window_analytics():
    """Test sliding window analytics endpoint"""
    response = client.get("/api/v1/analytics/sliding-window")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["aligned_quarter"] == "2025Q4_naive"
    assert data[1]["aligned_quarter"] == "2025Q4_aligned"

def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
