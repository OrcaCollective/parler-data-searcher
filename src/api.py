from quart import render_template
from quart_motor import Motor

from api_types import User


PAGE_LIMIT = 20


async def get_users(mongo: Motor, search_term: str, page: int) -> list[User]:
    skip = page * PAGE_LIMIT
    search_regex = {
        "$regex": f"^{search_term}*",
        "$options": "i",
    }
    results: list[User] = await mongo.db.users.find(
        {
            "$or": [
                {
                    "name": search_regex,
                },
                {
                    "username": search_regex,
                },
            ],
        },
        skip=skip,
        limit=PAGE_LIMIT,
    ).to_list(length=PAGE_LIMIT)

    return results


async def render_users(users: list[User]) -> str:
    return await render_template("users_results.jinja", users=users)
