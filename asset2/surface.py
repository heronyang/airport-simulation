import os
import json
import logging

from node import Node
from link import Link

class Surface:
    """
    Surface contains data structures for storing properties and objects within
    an airport, including its gates, spot positions, runways, etc.
    """

    def __init__(self, center, corners, image_filepath):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        self.gates = []
        self.spots = []
        self.runways = []
        self.taxiways = []

        self.center = center
        self.corners = corners
        self.image_filepath = image_filepath

    def __repr__(self):
        return "<Surface>"

    """
    Gets the node with its name and raises exception if no such node is found
    since we should always work on nodes that we know.
    """
    def get_node(self, name):

        # FIXME: a more efficient way can be implemented in the future
        for gate in self.gates:
            if gate.name == name:
                return gate

        for spot in self.spots:
            if spot.name == name:
                return spot

        raise Exception("Getting an unknown node")

    """
    Gets the link with its name and raises exception if no such link is found.
    """
    def get_link(self, name):

        # FIXME: a more efficient way can be implemented in the future
        for runway in self.runways:
            if runway.name == name:
                return runway

        for taxiway in self.taxiways:
            if taxiway.name == name:
                return taxiway

        raise Exception("Getting an unknown link")

    """
    Returns all links.
    """
    @property
    def links(self):
        return self.runways + self.taxiways

    """
    Returns all nodes.
    """
    @property
    def nodes(self):
        return self.gates + self.spots

    def print_stats(self):

        # Prints surface states
        self.logger.debug("%d gates, %d spots, %d runways, %d taxiways" %
                          (len(self.gates), len(self.spots), len(self.runways),
                           len(self.taxiways)))

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

class Taxiway(Link):

    def __init__(self, index, name, nodes):
        Link.__init__(self, index, name, nodes)

    def __repr__(self):
        return "<TAXIWAY: %s>" % self.name

class PushbackWay(Link):

    def __init__(self, index, name, nodes):
        Link.__init__(self, index, name, nodes)

    def __repr__(self):
        return "<PUSHBACKWAY: %s>" % self.name

class SurfaceFactory:
    """
    SurfaceFactory loads surface data files under `dir_path` and uses them for
    initializing a surface object . `FILES_TO_CHECK` is a list of required file
    for the surface object.
    """

    FILES_TO_CHECK = [
        "airport-metadata.json",
        "airport.jpg",
        "gates.json",
        "spots.json",
        "runways.json",
        "pushback_ways.json",
        "taxiways.json"
    ]

    @classmethod
    def create(self, dir_path):
        if not SurfaceFactory.__is_data_ready(dir_path):
            raise Exception("Surface data is not ready")
        with open(dir_path + "airport-metadata.json") as f:
            airport_raw = json.load(f)
        surface = Surface(airport_raw["center"], airport_raw["corners"],
                          dir_path + "airport.jpg")
        SurfaceFactory.__load_gates(surface, dir_path)
        SurfaceFactory.__load_spots(surface, dir_path)
        SurfaceFactory.__load_runway(surface, dir_path)
        SurfaceFactory.__load_taxiway(surface, dir_path)
        SurfaceFactory.__load_pushback_way(surface, dir_path)
        return surface

    @classmethod
    def __is_data_ready(self, dir_path):

        # Checks if the files exist
        for f in SurfaceFactory.FILES_TO_CHECK:
            file_path = dir_path + f
            if not os.path.exists(file_path):
                return False

        return True

    @classmethod
    def __load_gates(self, surface, dir_path):
        surface.gates = SurfaceFactory.__retrieve_node("gates", dir_path)

    @classmethod
    def __load_spots(self, surface, dir_path):
        surface.spots = SurfaceFactory.__retrieve_node("spots", dir_path)

    @classmethod
    def __retrieve_node(self, type_name, dir_path):

        nodes = []

        with open(dir_path + type_name + ".json") as f:
            nodes_raw = json.load(f)

        for node_raw in nodes_raw:
            if type_name == "spots":
                nodes.append(Spot(
                    node_raw["index"],
                    node_raw["name"],
                    {"lat": node_raw["lat"], "lng": node_raw["lng"]}
                ))
            elif type_name == "gates":
                nodes.append(Gate(
                    node_raw["index"],
                    node_raw["name"],
                    {"lat": node_raw["lat"], "lng": node_raw["lng"]}
                ))
            else:
                raise Exception("Unknown node type")

        return nodes

    @classmethod
    def __load_runway(self, surface, dir_path):
        surface.runways = SurfaceFactory.__retrive_link("runways", dir_path)

    @classmethod
    def __load_taxiway(self, surface, dir_path):
        surface.taxiways = SurfaceFactory.__retrive_link("taxiways", dir_path)

    @classmethod
    def __load_pushback_way(self, surface, dir_path):
        surface.pushback_ways = SurfaceFactory.__retrive_link("pushback_ways",
                                                              dir_path)

    @classmethod
    def __retrive_link(self, type_name, dir_path):

        links = []

        with open(dir_path + type_name + ".json") as f:
            links_raw = json.load(f)

        for link_raw in links_raw:

            index = link_raw["index"]
            name = link_raw["name"]

            nodes = []
            for node in link_raw["nodes"]:
                nodes.append(RunwayNode({"lat": node[1], "lng": node[0]}))

            if type_name == "runways":
                links.append(Runway(index, name, nodes))
            elif type_name == "taxiways":
                links.append(Taxiway(index, name, nodes))
            elif type_name == "pushback_ways":
                links.append(PushbackWay(index, name, nodes))
            else:
                raise Exception("Unknown link type")

        return links
