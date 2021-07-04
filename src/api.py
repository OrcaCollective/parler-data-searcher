import asyncio
import logging
from math import floor
from typing import Optional, Tuple, TypeVar
import re

from pymongo.errors import OperationFailure
from quart_motor import Motor

from api_types import User, Post
from constants import DB_USERS, DB_POSTS
from enums import SearchBehavior


T = TypeVar("T", Post, User)

logger = logging.getLogger(__name__)

PAGE_LIMIT = 20


def _normalize_username(username: str):
    return username if username.startswith("@") else f"@{username}"


def escape(s: str) -> str:
    return re.escape(s.strip())


def get_highlighter_regex(search_content: str) -> re.Pattern:
    return re.compile(f"({escape(search_content)})", re.IGNORECASE)


def get_match_any_regex(s: str) -> re.Pattern:
    return re.compile(f".*{escape(s)}.*", re.IGNORECASE)


def _username_contains_query(username: str) -> dict:
    # this username is not normalized because the search string can appear
    # anywhere inside a match, not just at the beginning
    search_regex = get_match_any_regex(username)

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


def _posts_by_user_query(username: str) -> Optional[dict]:
    if not username:  # avoid an empty $or clause which will cause an error
        return None

    formatted_username = _normalize_username(username)
    return {
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


def _posts_by_content_query(search_content: str) -> Optional[dict]:
    if not search_content:
        return None

    content_regex = get_match_any_regex(search_content)

    return {
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


def _gather_query_parts(*parts: Optional[dict]) -> Optional[list]:
    query_parts = [part for part in parts if part is not None]
    if len(query_parts) == 0:
        return None
    return query_parts


def _standard_query_logic(
    query_parts: Optional[list], behavior: SearchBehavior
) -> Optional[dict]:
    if query_parts is None:
        return None
    elif len(query_parts) == 1:
        query = query_parts[0]
    elif behavior == SearchBehavior.MATCH_ANY:
        query = {"$or": query_parts}
    elif behavior == SearchBehavior.MATCH_ALL:
        query = {"$and": query_parts}
    return query


def _search_posts_query(
    username: str, content: str, behavior: SearchBehavior
) -> Optional[dict]:
    query_parts = _gather_query_parts(
        _posts_by_user_query(username), _posts_by_content_query(content)
    )
    return _standard_query_logic(query_parts, behavior)


def _search_posts_with_mentions_query(
    username: str, content: str, behavior: SearchBehavior
) -> Optional[dict]:
    username_query = _posts_by_user_query(username)
    mention_query = _posts_by_content_query(username)
    content_query = _posts_by_content_query(content)
    if behavior == SearchBehavior.MATCH_ALL:
        mention_query_parts = _gather_query_parts(username_query, mention_query)
        subquery = _standard_query_logic(mention_query_parts, SearchBehavior.MATCH_ANY)
        query_parts = _gather_query_parts(content_query, subquery)
    else:
        query_parts = _gather_query_parts(username_query, mention_query, content_query)
    return _standard_query_logic(query_parts, behavior)


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
        logger.error(f"Failure retrieving {collection}: {err}", err)

        # probably an invalid regex, just return nothing
        total_count = 0
        results = []

    page_count = floor(total_count / PAGE_LIMIT) + 1

    return page_count, results


async def search_users(
    mongo: Motor, username: str, page: int
) -> Tuple[int, list[User]]:
    return await _get_entities(
        mongo, DB_USERS, _username_contains_query(username), page
    )


async def search_posts(
    mongo: Motor,
    username: str,
    content: str,
    page: int,
    behavior: SearchBehavior,
    mentions: bool,
) -> Tuple[int, list[Post]]:
    """
    Search for posts by username and/or content.

    :param mongo: A MongoDB Motor connection object.
    :param username: Username to search for.
    :param content: Content to search for.
    :param page: Page number of search query results to return.
    :param behavior: If SearchBehavior.MATCH_ANY, return content matching any
                     search field, if SearchBehavior.MATCH_ALL, return content
                     matching all search fields.
    :param mentions: If mentions is true, also include results where the username
                     is mentioned in the content field by any other user. Otherwise
                     just return relevent username matches.
    :return:
    """
    if mentions:
        query = _search_posts_with_mentions_query(username, content, behavior)
    else:
        query = _search_posts_query(username, content, behavior)
    page_count, results = await _get_entities(mongo, DB_POSTS, query, page)
    return page_count, results
