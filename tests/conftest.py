import pytest
from quart_rate_limiter.store import MemoryStore


@pytest.fixture
def app():
    from app import app, limiter

    limiter.store = MemoryStore()
    yield app
