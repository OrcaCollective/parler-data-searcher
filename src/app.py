#!/usr/bin/env python
from quart import Quart, render_template, request, redirect
from quart_motor import Motor
import os
from dotenv import load_dotenv
from urllib.parse import urlencode

import api
from constants import (
    POSTS_PATH_COMPONENT,
    USERNAME_QUERY_PARAM,
    SEARCH_CONTENT_QUERY_PARAM,
    USERS_PATH_COMPONENT,
    PAGE_QUERY_PARAM,
)
import templatefilters

load_dotenv()

MONGO_USER = os.environ.get("MONGO_USER")
MONGO_PASS = os.environ.get("MONGO_PASS")
MONGO_ENDPOINT = os.environ.get("MONGO_ENDPOINT")
MONGO_PORT = os.environ.get("MONGO_PORT")

app = Quart(__name__, static_folder="public", template_folder="views")

templatefilters.register_filters(app)

mongo = Motor(
    app, uri=f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_ENDPOINT}:{MONGO_PORT}/parler"
)


################################################################################
# Home page reroute
################################################################################
ROUTE_PARAMS = {
    "search_type",
}


@app.route("/")
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
async def about():
    return await render_template("about.html")


@app.route(f"/{POSTS_PATH_COMPONENT}", strict_slashes=False)
async def posts():
    username = request.args.get(USERNAME_QUERY_PARAM, "")
    search_content = request.args.get(SEARCH_CONTENT_QUERY_PARAM, "")
    page = request.args.get(PAGE_QUERY_PARAM, 0)
    try:
        page = int(page)
    except ValueError:
        page = 0

    if not username and not search_content:
        return await render_template("posts.html")

    page_count, results = await api.search_posts(mongo, username, search_content, page)

    return await render_template(
        "posts.html",
        posts=results,
        page=page,
        username=username,
        search_content=search_content,
        page_count=page_count,
        search_type=POSTS_PATH_COMPONENT,
    )


@app.route(f"/{USERS_PATH_COMPONENT}", strict_slashes=False)
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
