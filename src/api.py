import asyncio
import logging
from math import floor
from typing import Optional, Tuple

from pymongo.errors import OperationFailure
from quart_motor import Motor

from api_types import User, Post
from constants import DB_USERS, DB_POSTS
from enums import SearchBehavior

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


async def search_users(
    mongo: Motor, username: str, page: int
) -> Tuple[int, list[User]]:
    skip = page * PAGE_LIMIT
    query = _search_users_query(username)

    try:
        count_f = mongo.db[DB_USERS].count_documents(query)
        entities_f = (
            mongo.db[DB_USERS]
            .find(query)
            .skip(skip)
            .limit(PAGE_LIMIT)
            .to_list(length=PAGE_LIMIT)
        )

        await asyncio.wait({count_f, entities_f}, return_when=asyncio.FIRST_EXCEPTION)

        entities: list[User] = await entities_f
        page_count: int = floor(await count_f / PAGE_LIMIT) + 1

    except OperationFailure as err:
        logger.error(f"Failure retrieving {DB_USERS}: {err}", err)
        raise

    return page_count, entities


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
    count = -1

    # first, generate the query and, depending on the indicated search behavior,
    # perhaps the total document count as well
    if behavior == SearchBehavior.USERNAME_AGGRESSIVE:
        # if USERNAME_AGGRESSIVE, preferentially search for posts by a user,
        # or, if nothing can be found, search for any content containing that username.
        username_query = _search_posts_query(username, "")
        content_query = _search_posts_query("", username)

        try:
            count_username_f = mongo.db[DB_POSTS].count_documents(username_query)
            count_content_f = mongo.db[DB_POSTS].count_documents(content_query)

            await asyncio.wait(
                {count_username_f, count_content_f}, return_when=asyncio.FIRST_EXCEPTION
            )

            count_username = await count_username_f
            count_content = await count_content_f
        except OperationFailure as err:
            logger.error(
                f"Failed to get pre-flight post counts when searching aggressively: {err}",
                err,
            )
            raise

        if count_username > 0:
            query = username_query
            count = count_username
        elif count_content > 0:
            query = content_query
            count = count_content
        else:
            query = None
            count = 0
    else:
        query = _search_posts_query(username, content)

    # if we have a query, execute it
    if query is not None:
        try:
            if count < 0:
                count_f = mongo.db[DB_POSTS].count_documents(query)
            else:
                # in the event we already have the count,
                # generate a placeholder task that returns it
                async def dummy() -> int:
                    return count

                count_f = asyncio.create_task(dummy())

            skip = page * PAGE_LIMIT

            entities_f = (
                mongo.db[DB_POSTS]
                .find(query)
                .skip(skip)
                .limit(PAGE_LIMIT)
                .to_list(length=PAGE_LIMIT)
            )

            await asyncio.wait(
                {count_f, entities_f}, return_when=asyncio.FIRST_EXCEPTION
            )

            page_count: int = floor(await count_f / PAGE_LIMIT) + 1
            entities: list[Post] = await entities_f

            return page_count, entities
        except OperationFailure as err:
            logger.error(f"Failure retrieving {DB_POSTS}: {err}", err)
            raise
    else:
        return 0, []
