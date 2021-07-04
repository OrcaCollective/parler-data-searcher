import pytest
from quart_rate_limiter.store import MemoryStore


@pytest.fixture
def app():
    from app import limiter, app
    limiter.store = MemoryStore()
    yield app
