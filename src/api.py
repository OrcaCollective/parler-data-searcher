from quart import render_template
from quart_motor import Motor
from typing import Tuple
from math import floor

from api_types import User


PAGE_LIMIT = 20


def _get_users_query(search_term: str) -> dict:
    search_regex = {
        "$regex": f"^{search_term}*",
        "$options": "i",
    }

    query = {
        "$or": [
            {
                "name": search_regex,
            },
            {
                "username": search_regex,
            },
        ],
    }

    return query


async def get_users(
    mongo: Motor, search_term: str, page: int
) -> Tuple[int, list[User]]:
    skip = page * PAGE_LIMIT
    query = _get_users_query(search_term)
    total_count: int = await mongo.db.users.count_documents(query)
    page_count = floor(total_count / PAGE_LIMIT) + 1
    results: list[User] = (
        await mongo.db.users.find(query)
        .skip(skip)
        .limit(PAGE_LIMIT)
        .to_list(length=PAGE_LIMIT)
    )

    return page_count, results


async def render_users(users: list[User]) -> str:
    return await render_template("users_results.jinja", users=users)
