import os
import csv
import json

from node import Node
from link import Link
from IPython.core.debugger import Tracer

class Airport:
    """ Data structure for storing properties and objects within an airport,
    including its own name, geo information, surface data, etc.
    """

    gates = []
    spots = []
    runways = []

    def __init__(self, code, name, center, corners, image_filepath):
        self.code = code
        self.name = name
        self.center = center
        self.corners = corners
        self.image_filepath = image_filepath

    def __repr__(self):
        return "<Airport: %s>" % self.name

class Gate(Node):

    def __init__(self, index, name, geo_pos):
        Node.__init__(self, index, name, geo_pos)

    def __repr__(self):
        return "<GATE: %s>" % self.name

class Spot(Node):

    def __init__(self, index, name, geo_pos):
        Node.__init__(self, index, name, geo_pos)

    def __repr__(self):
        return "<SPOT: %s>" % self.name

class RunwayNode(Node):

    def __init__(self, geo_pos):
        Node.__init__(self, -1, "", geo_pos)

    def __repr__(self):
        return "<RUNWAY_NODE>"

class Runway(Link):

    def __init__(self, index, name, nodes):
        Link.__init__(self, index, name, nodes)

    def __repr__(self):
        return "<RUNWAY: %s>" % self.name

class Manager:

    DATA_ROOT_DIR_PATH = "./data/"
    FILES_TO_CHECK = [
        "airport-metadata.json",
        "airport.jpg",
        "gates.csv",
        "spots.csv"
    ]

    airport = None

    def __init__(self, iata_airport_code):

        # Checks if the airport folder/files are ready
        self.dir_path = self.DATA_ROOT_DIR_PATH + iata_airport_code + "/build/"
        if not self.is_data_ready():
            raise Exception("Airport %s data is not ready" % iata_airport_code)

        self.load_airport(iata_airport_code)
        self.load_gates()
        self.load_spots()
        self.load_runway()

    def is_data_ready(self):

        # Checks if the folder exists
        if not os.path.exists(self.dir_path):
            return False

        # Checks if the files exist
        for f in self.FILES_TO_CHECK:
            file_path = self.dir_path + f
            if not os.path.exists(file_path):
                return False

        return True

    def load_airport(self, iata_airport_code):
        with open(self.dir_path + "airport-metadata.json") as f:
            airport_md = json.load(f)
        self.airport = Airport(iata_airport_code, airport_md["name"],
                               airport_md["center"], airport_md["corners"],
                               self.DATA_ROOT_DIR_PATH + iata_airport_code +\
                               "/build/airport.jpg")

    def load_gates(self):

        gates = []
        self.retrieve_node_with_type(gates, "gates")
        self.airport.gates = gates

    def load_spots(self):

        spots = []
        self.retrieve_node_with_type(spots, "spots")
        self.airport.spots = spots

    def retrieve_node_with_type(self, nodes, type_name):

        with open(self.dir_path + type_name + ".csv") as f:
            reader = csv.reader(f, delimiter = ",")
            next(reader)    # Skips the header
            for row in reader:
                index, name, lat, lng =\
                        row[0], row[1], float(row[2]), float(row[3])
                nodes.append(Spot(index, name, {"lat": lat, "lng": lng}))

    def load_runway(self):

        runways = []
        with open(self.dir_path + "runways.json") as f:
            runways_raw = json.load(f)
            for runway_raw in runways_raw:
                # Composes one runway object
                index = runway_raw["index"]
                name = runway_raw["name"]
                nodes = []
                for node in runway_raw["nodes"]:
                    nodes.append(RunwayNode({"lat": node[1], "lng": node[0]}))
                runways.append(Runway(index, name, nodes))
        self.airport.runways = runways
