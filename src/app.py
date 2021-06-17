#!/usr/bin/env python
from quart import Quart, render_template, request, redirect
from quart_motor import Motor
from bson import json_util

import json
import os

import api

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


@app.route("/posts")
async def posts():
    post = await mongo.db.posts.find_one()
    return json.dumps(post, default=json_util.default), 200


@app.route("/users/<search_term>")
async def users(search_term):
    page = request.args.get("page", 0)
    try:
        page = int(page)
    except ValueError:
        page = 0

    page_count, results = await api.get_users(mongo, search_term, page)

    results_html = await api.render_users(results)

    return await render_template(
        "index.html",
        results_html=results_html,
        page=page,
        search_term=search_term,
        page_count=page_count,
    )


if __name__ == "__main__":
    app.run()
