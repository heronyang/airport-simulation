import os
import json
import logging

from node import Node
from link import Link
from utils import random_string
from config import Config


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
        self.pushback_ways = []

        self.center = center
        self.corners = corners
        self.image_filepath = image_filepath

    """
    One node that connects to a link in the middle is not connected; therefore,
    break_links is used for cutting at the middle point and building new links
    that connects nodes to links.
    """
    def break_links(self):

        # Retrieve all nodes and links
        all_nodes = self.nodes

        for link in all_links:
            all_nodes.append(link.start)
            all_nodes.append(link.end)

        # Cut at the middle of the link if a node is contained
        new_runways, new_taxiways, new_pushback_ways = [], [], []
        to_rm_runways, to_rm_taxiways, to_rm_pushback_ways = [], [], []

        for node in all_nodes:

            # Runways
            for runway in self.runways:
                if not runway.contains_node(node):
                    continue
                new_runways += self.break_at(runway, node)
                to_rm_runways.append(runway)

            # Taxiway
            for taxiway in self.taxiways:
                if not taxiway.contains_node(node):
                    continue
                new_taxiways += self.break_at(taxiway, node)
                to_rm_taxiways.append(taxiway)

            # Pushback ways
            for pushback_way in self.pushback_ways:
                if not pushback_way.contains_node(node):
                    continue
                new_pushback_ways += self.break_at(pushback_way, node)
                to_rm_pushback_ways.append(pushback_way)

        # Remove
        self.runways = remove_list_from_list(self.runways, to_rm_runways)
        self.taxiways = remove_list_from_list(self.taxiways, to_rm_taxiways)
        self.pushback_ways = remove_list_from_list(self.pushback_ways,
                                                   to_rm_pushback_ways)

        # Add
        self.runways += new_runways
        self.taxiways += new_taxiways
        self.pushback_ways += new_pushback_ways

    def remove_list_from_list(original_list, to_rm_list):
        return [i for i in original_list if i not in to_rm_list]

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

        for pushback_way in self.pushback_ways:
            if pushback_way.name == name:
                return pushback_way

        raise Exception("Getting an unknown link")

    """
    Returns all links.
    """
    @property
    def links(self):
        return self.runways + self.taxiways + self.pushback_ways

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

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)

    def set_quiet(self, logger):
        self.logger = logger


class Gate(Node):

    def __init__(self, name, geo_pos):
        Node.__init__(self, name, geo_pos)


class Spot(Node):

    def __init__(self, name, geo_pos):
        Node.__init__(self, name, geo_pos)


class RunwayNode(Node):

    def __init__(self, geo_pos):
        Node.__init__(self, "", geo_pos)


class Runway(Link):

    def __init__(self, name, nodes):
        Link.__init__(self, name, nodes)

    def __repr__(self):
        return "<RUNWAY: %s>" % self.name


class Taxiway(Link):

    def __init__(self, name, nodes):
        Link.__init__(self, name, nodes)

    def __repr__(self):
        return "<TAXIWAY: %s>" % self.name


class PushbackWay(Link):

    def __init__(self, name, nodes):
        Link.__init__(self, name, nodes)

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

            name = node_raw["name"]
            if name is None or len(name) == 0:
                name = "n-" + random_string(
                            Config.params["simulation"]["random_name_length"])

            if type_name == "spots":
                nodes.append(Spot(name,
                    {"lat": node_raw["lat"], "lng": node_raw["lng"]}
                ))
            elif type_name == "gates":
                nodes.append(Gate(name,
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

            name = link_raw["name"]
            if name is None or len(name) == 0:
                name = "l-" + random_string(
                            Config.params["simulation"]["random_name_length"])

            nodes = []
            for node in link_raw["nodes"]:
                nodes.append(RunwayNode({"lat": node[1], "lng": node[0]}))

            if type_name == "runways":
                links.append(Runway(name, nodes))
            elif type_name == "taxiways":
                links.append(Taxiway(name, nodes))
            elif type_name == "pushback_ways":
                links.append(PushbackWay(name, nodes))
            else:
                raise Exception("Unknown link type")

        return links
