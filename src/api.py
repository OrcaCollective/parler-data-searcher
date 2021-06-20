from quart_motor import Motor
from typing import Tuple, Type, TypeVar
from math import floor
from pymongo.errors import OperationFailure

import logging
import asyncio

T = TypeVar("T")


logger = logging.getLogger(__name__)


PAGE_LIMIT = 20


def get_users_query(search_term: str) -> dict:
    search_regex = {
        "$regex": f".*{search_term}.*",
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


def get_post_query(search_term: str) -> dict:
    search_regex = {
        "$regex": f".*{search_term}.*",
        "$options": "i",
    }

    return {
        "$or": [
            {
                "username": search_regex,
            },
            {
                "comments.username": search_regex,
            },
            {
                "echo.username": search_regex,
            },
        ],
    }


async def get_entities(
    mongo: Motor, collection: str, query: dict, page: int, entity: Type[T]
) -> Tuple[int, list[T]]:
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
        # indiscriminantly await each future, if one failed then the exception will raise as expected
        total_count: int = await total_count_f
        results: list[T] = await results_f
    except OperationFailure as err:
        logger.error(f"Failure retrieving {collection}: {err}")

        # probably an invalid regex, just return nothing
        total_count = 0
        results = []

    page_count = floor(total_count / PAGE_LIMIT) + 1

    return page_count, results
