#!/usr/bin/env python3
import os
import json
from flask import Flask, request, abort
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulator import init_streaming_generator

dir_path = os.path.dirname(os.path.realpath(__file__)) + "/../"
AIRPORT_DATA_FOLDER = dir_path + "data/"
PLAN_INPUT_FOLDER = dir_path + "plans/"
PLAN_OUTPUT_FOLDER = dir_path + "output/"

app = Flask(__name__, static_url_path="")

# WORKAROUND: Since Flask does not support object storage in sessions,
# use a dictionary to store the generator for each client.
# A simulator ID is used to identify these clients.
simulators = {}


@app.route("/")
def send_index():
    return app.send_static_file("index.html")


# Get Plans
@app.route("/plans/batch")
def api_batch_plans():
    return json.dumps(sorted(
        [f for f in next(os.walk(PLAN_OUTPUT_FOLDER))[1]]))


@app.route("/plans/streaming")
def api_streaming_plans():
    plans = [f for f in next(os.walk(PLAN_INPUT_FOLDER))[2]]
    plans = map(lambda p: p.split(".")[0], list(filter(lambda p: "yaml" in p, plans)))
    return json.dumps(sorted(plans))


# Get Data
@app.route("/data/batch")
def api_batch_data():
    try:
        plan = request.args.get("plan")
        airport = get_airport_from_plan(plan)

        if plan is None:
            abort(400, description="Invalid parameter")

        return json.dumps({
            "surface": get_surface_data(airport),
            "state": get_state_data(plan)
        })

    except Exception as e:
        abort(400, description=str(e))


@app.route("/data/streaming")
def api_streaming_data():
    try:
        # Init
        global simulators
        simulator_id = int(request.args.get("id"))

        if simulator_id < 0:
            plan = request.args.get("plan")

            if plan is None:
                abort(400, description="Invalid parameter")

            simulator, airport = init_streaming_generator(plan)

            simulator_id = int(round(time.time() * 1000))
            simulators[simulator_id] = simulator

            return json.dumps({
                "surface": get_surface_data(airport),
                "state": [next(simulator)],
                "simulatorId": simulator_id
            })

        else:
            steps = int(request.args.get("steps"))
            state = []
            for i in range(steps):
                try:
                    state.append(next(simulators[simulator_id]))
                except StopIteration:
                    break

            return json.dumps(state)

    except Exception as e:
        abort(400, description=str(e))


def get_airport_from_plan(plan):
    filename = PLAN_OUTPUT_FOLDER + plan + "/airport.txt"
    if not os.path.isfile(filename):
        raise Exception("Airport name not found at %s" % filename)
    with open(filename) as f:
        airport = f.read().strip()
    return airport


def get_surface_data(airport):
    airport_data_folder = AIRPORT_DATA_FOLDER + airport + "/"

    airport_name, airport_center = get_airport_metadata(airport_data_folder)
    pushback_ways = get_linknode_data(airport_data_folder, "pushback_ways")
    taxiways = get_linknode_data(airport_data_folder, "taxiways")
    runways = get_linknode_data(airport_data_folder, "runways")
    gates = get_linknode_data(airport_data_folder, "gates")
    spots = get_linknode_data(airport_data_folder, "spots")

    return {
        "airport_name": airport_name,
        "airport_center": airport_center,
        "pushback_ways": pushback_ways,
        "taxiways": taxiways,
        "runways": runways,
        "gates": gates,
        "spots": spots
    }


def get_airport_metadata(airport_data_folder):
    filename = airport_data_folder + "build/airport-metadata.json"
    if not os.path.isfile(filename):
        raise Exception("Airport data not found at %s" % filename)

    with open(filename) as f:
        d = json.loads(f.read())
        name = d["name"]
        center = d["center"]

    return name, center


def get_linknode_data(airport_data_folder, name):
    filename = airport_data_folder + "build/" + name + ".json"
    if not os.path.isfile(filename):
        raise Exception("Link data not found at %s" % filename)

    with open(filename) as f:
        links = json.loads(f.read())
    return links


def get_state_data(plan):
    # Finds the state file
    filename = PLAN_OUTPUT_FOLDER + plan + "/states.json"
    if not os.path.isfile(filename):
        raise Exception("State file not found at %s" % filename)

    # Reads the file
    with open(filename) as f:
        content = [json.loads(j) for j in f.read().split("\n") if j]
    return content


if __name__ == "__main__":
    app.run(host="0.0.0.0")
