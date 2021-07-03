import pytest
from unittest.mock import patch

from app import app

from tests.utils.posts import make_post
from tests.utils.users import make_user


@pytest.mark.asyncio
async def test_index_route():
    client = app.test_client()
    response = await client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_users_route():
    client = app.test_client()
    response = await client.get("/users")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_posts_route():
    client = app.test_client()
    response = await client.get("/posts")
    assert response.status_code == 200


@pytest.mark.asyncio
@patch("api.search_users")
async def test_users_route_retrieves_no_users(mock_search_users):
    mock_search_users.return_value = (0, [])
    client = app.test_client()
    response = await client.get("/users?username=test-username")
    assert response.status_code == 200
    data = str(await response.data)
    assert "No results found for this query" in data


@pytest.mark.asyncio
@patch("api.search_posts")
async def test_posts_route_retrieves_no_posts(mock_search_posts):
    mock_search_posts.return_value = (0, [])
    client = app.test_client()
    response = await client.get("/posts?username=test-username")
    assert response.status_code == 200
    data = str(await response.data)
    assert "No results found for this query" in data


@pytest.mark.asyncio
@patch("api.search_users")
async def test_users_route_one_page_users(mock_search_users):
    mock_search_users.return_value = (
        1,
        [make_user(f"@test_username_{i}", f"test-name-{i}") for i in range(20)],
    )
    client = app.test_client()
    response = await client.get("/users?username=test-username")
    assert response.status_code == 200
    data = str(await response.data)
    for i in range(20):
        assert (
            f'Username:</strong> <a href="/posts?username=%40test_username_{i}">@test_username_{i}</a>'
            in data
        )
        assert f"Name:</strong> test-name-{i}" in data


@pytest.mark.asyncio
@patch("api.search_posts")
async def test_posts_route_one_page_posts(mock_search_posts):
    mock_search_posts.return_value = (
        1,
        [
            make_post(f"test-username-{i}", f"test-post-text-{i}", [], None, None)
            for i in range(20)
        ],
    )
    client = app.test_client()
    response = await client.get("/posts?username=test-username")
    assert response.status_code == 200
    data = str(await response.data)
    for i in range(20):
        assert f"Username:</strong> test-username-{i}" in data
        assert f"Content:</strong> test-post-text-{i}" in data
        assert "Comments:</strong>" not in data


@pytest.mark.asyncio
@patch("api.search_posts")
async def test_posts_route_one_page_posts_highlight(mock_search_posts):
    mock_search_posts.return_value = (
        1,
        [
            make_post(f"test-username-{i}", f"test-post-text-{i}", [], None, None)
            for i in range(20)
        ],
    )
    client = app.test_client()
    response = await client.get(
        "/posts?username=test-username&search_content=test-post-text"
    )
    assert response.status_code == 200
    data = str(await response.data)
    for i in range(20):
        assert f"Username:</strong> test-username-{i}" in data
        assert f"Content:</strong> <mark>test-post-text</mark>-{i}" in data
        assert "Comments:</strong>" not in data
