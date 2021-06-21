import pytest
from app import app


@pytest.mark.asyncio
async def test_index_route():
    client = app.test_client()
    response = await client.get("/")
    assert response.status_code == 200
