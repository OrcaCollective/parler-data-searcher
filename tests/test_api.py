import pytest
import re
from unittest.mock import patch
from unittest.mock import MagicMock

import api
from enums import SearchBehavior


@pytest.mark.asyncio
@patch("api._get_entities")
async def test_search_posts_with_mentions(get_entities):
    get_entities.return_value = 0, []
    mongo = MagicMock()
    username = "@test_username"
    content = "test_content"

    await api.search_posts(
        mongo, username, content, 0, SearchBehavior.MATCH_ALL, mentions=True
    )

    content_regex = {
        "$regex": f".*{content}.*",
        "$options": "i",
    }

    mentions_regex = {
        "$regex": f".*{username}.*",
        "$options": "i",
    }

    query = {
        "$and": [
            {
                "$or": [
                    {
                        "text": content_regex,
                    },
                    {
                        "media.title": content_regex,
                    },
                    {
                        "comment.text": content_regex,
                    },
                    {
                        "echo.text": content_regex,
                    },
                ],
            },
            {
                "$or": [
                    {
                        "$or": [
                            {
                                "username": username,
                            },
                            {
                                "comments.username": username,
                            },
                            {"echo.username": username},
                        ],
                    },
                    {
                        "$or": [
                            {
                                "text": mentions_regex,
                            },
                            {
                                "media.title": mentions_regex,
                            },
                            {
                                "comment.text": mentions_regex,
                            },
                            {
                                "echo.text": mentions_regex,
                            },
                        ],
                    },
                ],
            },
        ],
    }

    get_entities.assert_called_once_with(mongo, "posts", query, 0)


def test_search_posts_query_returns_None():
    assert api._search_posts_query("", "", SearchBehavior.MATCH_ALL) is None


def test_search_post_query_returns_only_username_query():
    test_username = "@test-username"

    assert api._search_posts_query("test-username", "", SearchBehavior.MATCH_ALL) == {
        "$or": [
            {
                "username": test_username,
            },
            {
                "comments.username": test_username,
            },
            {
                "echo.username": test_username,
            },
        ],
    }


def test_search_post_query_returns_only_content_query():
    test_content_search = "test content search"
    content_regex = {
        "$regex": f".*{api.escape(test_content_search)}.*",
        "$options": "i",
    }

    assert api._search_posts_query(
        "", test_content_search, SearchBehavior.MATCH_ALL
    ) == {
        "$or": [
            {
                "text": content_regex,
            },
            {
                "media.title": content_regex,
            },
            {
                "comment.text": content_regex,
            },
            {
                "echo.text": content_regex,
            },
        ],
    }


def test_search_post_query_returns_full_query():
    test_username = "@test-username"
    test_content_search = "test content search"
    content_regex = {
        "$regex": f".*{api.escape(test_content_search)}.*",
        "$options": "i",
    }

    assert api._search_posts_query(
        "test-username", test_content_search, SearchBehavior.MATCH_ALL
    ) == {
        "$and": [
            {
                "$or": [
                    {
                        "username": test_username,
                    },
                    {
                        "comments.username": test_username,
                    },
                    {
                        "echo.username": test_username,
                    },
                ],
            },
            {
                "$or": [
                    {
                        "text": content_regex,
                    },
                    {
                        "media.title": content_regex,
                    },
                    {
                        "comment.text": content_regex,
                    },
                    {
                        "echo.text": content_regex,
                    },
                ],
            },
        ],
    }


def test_escape_trims_whitespace():
    assert api.escape(" ") == ""


def test_escape_escapes_regex_special_chars():
    assert api.escape("+") == r"\+"


def test_get_content_regex_escapes_search_content():
    assert api.get_content_regex("+") == re.compile(r"(\+)", re.IGNORECASE)
