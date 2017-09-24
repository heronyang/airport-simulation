#!/usr/bin/env python
import json

def generate_nodes(items):

    """
    Excepted a output file called `nodes.txt` containing:
    <X-Coord> <Y-Coord> <SOOS Node Num> <SMS Name> <SOSS Node Type> <Orignal ID>
    
    - splited by spaces or tabs
    - ordered by <SOSS Node Num>
    - <Original ID> won't be used for nodes.py

    In current nodes.py, only two types of node are supported: GATE_NODE and
    SPOT_NODE. Here, we map nodes with "aeroway": "gate" to GATE_NODE, but we
    couldn't find a SPOT_NODE data in current data set.
    """

    header = ["X Coord", "Y Coord", "Node Num", "Node Type", "Openstreetmap Id"]
    output_filename = "nodes.txt"
    nodes = []

    # Finds gate nodes
    index = 0
    node_type = "GATE_NODE"
    for item in items:
        # Filters out other items
        if item["properties"]["aeroway"] != "gate":
            continue
        x_coord = item["geometry"]["coordinates"][0]
        y_coord = item["geometry"]["coordinates"][1]
        os_id = item["id"].split("/")[1]
        nodes.append([x_coord, y_coord, index, node_type, os_id])
        index += 1

    export_to_file(output_filename, header, nodes)

def export_to_file(filename, header, data):
    f = open(filename, "w")
    f.write("\t".join(header) + "\n")
    for d in data:
        f.write(("\t".join(str(i) for i in d)) + "\n")
    f.close()

if __name__ == "__main__":

    with open("surface.json") as f:    

        surface_data = json.load(f)
        items = surface_data["features"]

        print("Generating node data")
        generate_nodes(items)
        print("Node data generated")
