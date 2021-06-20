#!/usr/bin/env python
from quart import Quart, render_template, request, redirect
from quart_motor import Motor
import os
from dotenv import load_dotenv

from api_types import User, Post
import api

load_dotenv()

MONGO_USER = os.environ.get("MONGO_USER")
MONGO_PASS = os.environ.get("MONGO_PASS")
MONGO_ENDPOINT = os.environ.get("MONGO_ENDPOINT")
MONGO_PORT = os.environ.get("MONGO_PORT")

app = Quart(__name__, static_folder="public", template_folder="views")

mongo = Motor(
    app, uri=f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_ENDPOINT}:{MONGO_PORT}/parler"
)


################################################################################
# Home page reroute
################################################################################
@app.route("/")
async def home():
    search_term = request.args.get("search_term")

    if search_term is not None:
        search_type = request.args.get("search_type", "users")
        page = request.args.get("page", 0)
        return redirect(f"/{search_type}/{search_term}?page={page}")

    return await render_template("index.html")


@app.route("/posts", defaults={"search_term": ""}, strict_slashes=False)
@app.route("/posts/<search_term>")
async def posts(search_term):
    page = request.args.get("page", 0)
    try:
        page = int(page)
    except ValueError:
        page = 0

    if not search_term:
        return await render_template("index.html")

    page_count, results = await api.get_entities(
        mongo,
        "posts",
        api.get_post_query(search_term),
        page,
        Post,
    )

    return await render_template(
        "posts.html",
        posts=results,
        page=page,
        search_term=search_term,
        page_count=page_count,
        search_type="posts",
    )


@app.route("/users", defaults={"search_term": ""}, strict_slashes=False)
@app.route("/users/<search_term>")
async def users(search_term):
    page = request.args.get("page", 0)
    try:
        page = int(page)
    except ValueError:
        page = 0

    if not search_term:
        return await render_template("index.html")

    page_count, results = await api.get_entities(
        mongo,
        "users",
        api.get_users_query(search_term),
        page,
        User,
    )

    return await render_template(
        "users.html",
        users=results,
        page=page,
        search_term=search_term,
        page_count=page_count,
        search_type="users",
    )


if __name__ == "__main__":
    app.run()
