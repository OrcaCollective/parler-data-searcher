#!/usr/bin/env python
from flask import Flask, render_template


app = Flask(__name__, static_folder="public", template_folder="views")


################################################################################
# Home page reroute
################################################################################
@app.route("/")
def home():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
