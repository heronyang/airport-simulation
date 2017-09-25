#!/usr/bin/env python
import json
import csv
from map_adapter import MapAdapter

"""
This script generates files needed by the simulation including nodes.csv,
lines.csv, etc, by reading from source data files.
"""

def generate_gates_data(items):

    header = ["index", "name", "lat", "lng"]
    nodes = []

    # Finds gate nodes
    for item in items:
        # Filters out other items
        if item["properties"]["aeroway"] != "gate":
            continue
        index = item["id"].split("/")[1]
        name = item["properties"]["ref"]
        lat = item["geometry"]["coordinates"][1]
        lng = item["geometry"]["coordinates"][0]
        nodes.append([index, name, lat, lng])

    output_filename = "gates.csv"
    export_to_csv(output_filename, header, nodes)

def generate_airport_data(items):

    # Finds out the airport raw data from items
    airport_raw = None
    for item in items:
        if item["properties"]["aeroway"] == "aerodrome":
            airport_raw = item
            break
    if not airport_raw:
        raise Exception("Airport metadata is not found")

    map_adapter = MapAdapter()
    center = get_center(airport_raw["geometry"]["coordinates"][0])
    corners = map_adapter.center2corners(center)
    airport = {
        "name": airport_raw["properties"]["name"],
        "center": center,
        "corners": corners
    }

    # Export data to file
    filename = "airport-metadata.json"
    export_to_json(filename, airport)

    # Downloads the map
    filename = "airport.jpg"
    map_adapter.download(filename, center)

def get_center(coordinates):

    # NOTE: this won't work if the area across lat = 0 line

    most_west = coordinates[0][0]
    most_east = coordinates[0][0]
    most_north = coordinates[0][1]
    most_south = coordinates[0][1]

    for c in coordinates:
        most_west = min(most_west, c[0])
        most_east = max(most_east, c[0])
        most_north = max(most_north, c[1])
        most_south = min(most_south, c[1])

    return {
        "lat": (most_north + most_south) / 2,
        "lng": (most_west + most_east) / 2
    }

def export_to_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

def export_to_csv(filename, header, data):

    with open(filename, "wb") as f:
        writer = csv.writer(f, delimiter = ",")
        writer.writerow(header)
        writer.writerows(data)

if __name__ == "__main__":

    with open("surface.json") as f:    
        surface_data = json.load(f)
        items = surface_data["features"]

        print("Generating airport metadata")
        generate_airport_data(items)
        print("Airport metadata generated")

        print("Generating gate data")
        generate_gates_data(items)
        print("Gate data generated")
