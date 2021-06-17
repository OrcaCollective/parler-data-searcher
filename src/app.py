#!/usr/bin/env python
from quart import Quart, render_template
from bson import json_util

from connection import db

import json

app = Quart(__name__, static_folder="public", template_folder="views")


################################################################################
# Home page reroute
################################################################################
@app.route("/")
async def home():
    return await render_template("index.html")


@app.route("/posts")
async def posts():
    return json.dumps(db.posts.find_one(), default=json_util.default), 200


@app.route("/users")
async def users():
    return json.dumps(db.users.find_one(), default=json_util.default), 200


if __name__ == "__main__":
    app.run()
