#!/usr/bin/env python
from quart import Quart, render_template
from quart_motor import Motor
from bson import json_util

import json
import os

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
    return await render_template("index.html")


@app.route("/posts")
async def posts():
    post = await mongo.db.posts.find_one()
    return json.dumps(post, default=json_util.default), 200


@app.route("/users")
async def users():
    return json.dumps(await mongo.db.users.find_one(), default=json_util.default), 200


if __name__ == "__main__":
    app.run()
