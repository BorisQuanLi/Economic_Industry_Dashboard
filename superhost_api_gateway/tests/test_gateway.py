import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

@pytest.mark.asyncio
async def test_graphql_introspection():
    # Introspection is key for frontend/backend alignment
    query = "{ __schema { types { name } } }"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert "data" in response.json()

