#!/usr/bin/env python
from quart import Quart, render_template


app = Quart(__name__, static_folder="public", template_folder="views")


################################################################################
# Home page reroute
################################################################################
@app.route("/")
async def home():
    return await render_template("index.html")


if __name__ == "__main__":
    app.run()
