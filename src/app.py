#!/usr/bin/env python
import os
from datetime import timedelta
from typing import Optional
from urllib.parse import urlencode

from dotenv import load_dotenv
from quart import Quart, redirect, render_template, request
from quart_motor import Motor
from quart_rate_limiter import RateLimiter, rate_limit
from quart_rate_limiter.redis_store import RedisStore
from quart_rate_limiter.store import MemoryStore

import api
import templatefilters
from constants import (
    INCLUDE_MENTIONS_QUERY_PARAM,
    PAGE_QUERY_PARAM,
    POSTS_PATH_COMPONENT,
    SEARCH_BEHAVIOR_QUERY_PARAM,
    SEARCH_CONTENT_QUERY_PARAM,
    USERNAME_QUERY_PARAM,
    USERS_PATH_COMPONENT,
)
from enums import SearchBehavior


load_dotenv()

QUART_ENV = os.environ.get("QUART_ENV")
MONGO_USER = os.environ.get("MONGO_USER")
MONGO_PASS = os.environ.get("MONGO_PASS")
MONGO_ENDPOINT = os.environ.get("MONGO_ENDPOINT")
MONGO_PORT = os.environ.get("MONGO_PORT")
REDIS_URL = os.environ.get("REDIS_URL")

app = Quart(__name__, static_folder="public", template_folder="views")

templatefilters.register_filters(app)

mongo = Motor(
    app, uri=f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_ENDPOINT}:{MONGO_PORT}/parler"
)

if QUART_ENV == "development":
    redis_store = MemoryStore()
else:
    redis_store = RedisStore(REDIS_URL)


async def key_function() -> Optional[str]:
    return request.headers.get("X-Forwarded-For", request.remote_addr)


limiter = RateLimiter(app, key_function=key_function, store=redis_store)


@app.errorhandler(429)
async def limited(exc):
    return await render_template("429.html")


@app.errorhandler(404)
async def not_found(exc):
    return await render_template("404.html")


ROUTE_PARAMS = {
    "search_type",
}


@app.route("/")
@rate_limit(1, timedelta(milliseconds=500))
async def home():
    search_type = request.args.get("search_type")

    if search_type is not None:
        query_params = urlencode(
            {k: v for k, v in request.args.items() if k not in ROUTE_PARAMS}
        )
        return redirect(f"/{search_type}?{query_params}")

    # by default just render the users search
    return await render_template("users.html")


@app.route("/about", strict_slashes=False)
@rate_limit(1, timedelta(milliseconds=500))
async def about():
    return await render_template("about.html")


@app.route(f"/{POSTS_PATH_COMPONENT}", strict_slashes=False)
@rate_limit(1, timedelta(seconds=3))
async def posts():
    username = request.args.get(USERNAME_QUERY_PARAM, "")
    search_content = request.args.get(SEARCH_CONTENT_QUERY_PARAM, "")
    page = request.args.get(PAGE_QUERY_PARAM, 0)
    behavior = request.args.get(SEARCH_BEHAVIOR_QUERY_PARAM, "")
    mentions = request.args.get(INCLUDE_MENTIONS_QUERY_PARAM, "") == "true"

    try:
        behavior = SearchBehavior(behavior)
    except ValueError:
        behavior = SearchBehavior.MATCH_ALL

    try:
        page = int(page)
    except ValueError:
        page = 0

    if not username and not search_content:
        return await render_template("posts.html")

    page_count, results = await api.search_posts(
        mongo, username, search_content, page, behavior, mentions
    )

    highlighter_regex = None
    if search_content:
        highlighter_regex = api.get_highlighter_regex(search_content)

    return await render_template(
        "posts.html",
        posts=results,
        page=page,
        username=username,
        search_content=search_content,
        behavior=behavior.value,
        mentions=mentions,
        page_count=page_count,
        search_type=POSTS_PATH_COMPONENT,
        highlighter_regex=highlighter_regex,
    )


@app.route(f"/{USERS_PATH_COMPONENT}", strict_slashes=False)
@rate_limit(1, timedelta(seconds=1))
async def users():
    username = request.args.get(USERNAME_QUERY_PARAM)
    page = request.args.get(PAGE_QUERY_PARAM, 0)
    try:
        page = int(page)
    except ValueError:
        page = 0

    if not username:
        return await render_template("users.html")

    page_count, results = await api.search_users(mongo, username, page)

    return await render_template(
        "users.html",
        users=results,
        page=page,
        username=username,
        page_count=page_count,
        search_type=USERS_PATH_COMPONENT,
    )


if __name__ == "__main__":
    app.run()
