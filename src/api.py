import asyncio
import logging
from math import floor
from typing import Optional, Tuple, TypeVar

from pymongo.errors import OperationFailure
from quart_motor import Motor

from api_types import User, Post
from constants import DB_USERS, DB_POSTS
from enums import SearchBehavior


T = TypeVar("T", User, Post)

logger = logging.getLogger(__name__)

PAGE_LIMIT = 20


def _search_users_query(username: str) -> dict:
    search_regex = {
        "$regex": f".*{username}.*",
        "$options": "i",
    }

    return {
        "$or": [
            {
                "name": search_regex,
            },
            {
                "username": search_regex,
            },
        ],
    }


def _search_posts_query(username: str, search_content: str) -> Optional[dict]:
    username_query = {}
    if username:
        formatted_username = username if username.startswith("@") else f"@{username}"
        username_query = {
            "$or": [
                {
                    "username": formatted_username,
                },
                {
                    "comments.username": formatted_username,
                },
                {
                    "echo.username": formatted_username,
                },
            ],
        }

    content_query = {}
    if search_content:
        content_regex = {
            "$regex": f".*{search_content}.*",
            "$options": "i",
        }
        content_query = {
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

    # avoid an empty $or clause which will cause an error
    if not username_query and not content_query:
        return None

    if username_query and not content_query:
        return username_query

    if content_query and not username_query:
        return content_query

    return {"$and": [username_query, content_query]}


async def _get_entities(
    mongo: Motor,
    collection: str,
    query: Optional[dict],
    page: int,
) -> Tuple[int, list[T]]:
    if query is None:
        return 0, []

    skip = page * PAGE_LIMIT

    try:
        total_count_f = mongo.db[collection].count_documents(query)
        results_f = (
            mongo.db[collection]
            .find(query)
            .skip(skip)
            .limit(PAGE_LIMIT)
            .to_list(length=PAGE_LIMIT)
        )
        await asyncio.wait(
            {total_count_f, results_f}, return_when=asyncio.FIRST_EXCEPTION
        )
        # indiscriminately await each future, if one failed then the exception will raise as expected
        total_count: int = await total_count_f
        results: list[T] = await results_f
    except OperationFailure as err:
        logger.error(f"Failure retrieving {collection}: {err}")

        # probably an invalid regex, just return nothing
        total_count = 0
        results = []

    page_count = floor(total_count / PAGE_LIMIT) + 1

    return page_count, results


async def search_users(
    mongo: Motor, username: str, page: int
) -> Tuple[int, list[User]]:
    return await _get_entities(mongo, DB_USERS, _search_users_query(username), page)


async def search_posts(
    mongo: Motor, username: str, content: str, page: int, behavior: SearchBehavior
) -> Tuple[int, list[Post]]:
    """
    Search for posts by username and/or content.

    :param mongo:
    :param username:
    :param content:
    :param page:
    :param behavior: If SearchBehavior.USERNAME_AGGRESSIVE, content will be ignored.
    :return:
    """
    query = None

    # first, sniff what query we need to use
    if behavior == SearchBehavior.USERNAME_AGGRESSIVE:
        # if USERNAME_AGGRESSIVE, preferentially search for posts by a user,
        # or, if nothing can be found, search for any content containing that username.
        username_query = _search_posts_query(username, "")
        content_query = _search_posts_query("", username)

        try:
            username_present_f = mongo.db[DB_POSTS].find_one(username_query)
            content_present_f = mongo.db[DB_POSTS].find_one(content_query)

            await asyncio.wait(
                {username_present_f, content_present_f},
                return_when=asyncio.FIRST_EXCEPTION,
            )

            username_present = await username_present_f
            content_present = await content_present_f
        except OperationFailure as err:
            logger.error(
                f"Failed to get pre-flight post counts when searching aggressively: {err}",
                err,
            )
            raise

        if username_present:
            query = username_query
        elif content_present:
            query = content_query
        else:
            query = None
    else:
        query = _search_posts_query(username, content)

    # if we have a query, execute it
    if query is not None:
        return await _get_entities(mongo, DB_POSTS, query, page)
    else:
        return 0, []
