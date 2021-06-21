import api


def test_search_post_query_returns_None():
    assert api._search_posts_query("", "") is None


def test_search_post_query_returns_only_username_query():
    test_username = "@test-username"

    assert api._search_posts_query("test-username", "") == {
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
        "$regex": f".*{test_content_search}.*",
        "$options": "i",
    }

    assert api._search_posts_query("", test_content_search) == {
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
        "$regex": f".*{test_content_search}.*",
        "$options": "i",
    }

    assert api._search_posts_query("test-username", test_content_search) == {
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