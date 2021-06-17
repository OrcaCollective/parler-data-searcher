from quart_motor import Motor
from typing import Tuple
from math import floor
from pymongo.errors import OperationFailure

import logging
import sys

from api_types import User


logger = logging.getLogger(__name__)


PAGE_LIMIT = 20


def _get_users_query(search_term: str) -> dict:
    search_regex = {
        "$regex": f".*{search_term}.*",
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

    try:
        total_count: int = await mongo.db.users.count_documents(query)
        results: list[User] = (
            await mongo.db.users.find(query)
            .skip(skip)
            .limit(PAGE_LIMIT)
            .to_list(length=PAGE_LIMIT)
        )
    except OperationFailure:
        _, exc, _ = sys.exc_info()
        logger.error(exc)

        # probably an invalid regex, just return nothing
        total_count = 0
        results = []

    page_count = floor(total_count / PAGE_LIMIT) + 1

    return page_count, results
