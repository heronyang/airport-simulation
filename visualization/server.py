#!/usr/bin/env python3
import os
import json
from flask import Flask

dir_path = os.path.dirname(os.path.realpath(__file__))
AIRPORT_DATA_FOLDER = dir_path + "/../data/"
PLAN_OUTPUT_FOLDER = dir_path + "/../output/"

app = Flask(__name__, static_url_path="")

@app.route("/")
def send_index():
    return app.send_static_file("index.html")

@app.route("/airports")
def api_airports():
    return json.dumps([f for f in next(os.walk(AIRPORT_DATA_FOLDER))[1]])

@app.route("/plans")
def api_plans():
    return json.dumps([f for f in next(os.walk(PLAN_OUTPUT_FOLDER))[1]])

if __name__ == "__main__":
    app.run(debug=True)
