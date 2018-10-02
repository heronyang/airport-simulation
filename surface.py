"""An airport surface is represented in `Surface` containing the subcomponents
including gates, spot positions, runways, etc. The subcomponents are extended
on top of the link-node model.
"""
import os
import json
import logging
import cache

from node import Node
from link import Link
from config import Config


class Surface:
    """Surface contains data structures for storing properties and objects
    within an airport, including its gates, spot positions, runways, etc.
    """

    def __init__(self, center, corners, image_filepath):

        self.logger = logging.getLogger(__name__)

        self.gates = []
        self.spots = []
        self.runways = []
        self.taxiways = []
        self.pushback_ways = []

        self.center = center
        self.corners = corners
        self.image_filepath = image_filepath

        self.break_nodes = set([])

    def break_links(self):
        """ One node that connects to a link in the middle is not connected;
        therefore, break_links is used for cutting at the middle point and
        building new links that connects nodes to links.
        """

        self.logger.info("Starts to break links")
        cache_enabled = Config.params["simulation"]["cache"]

        # Loads all_nodes from cache if exists
        if cache_enabled:
            hash_key = cache.get_hash([], self.nodes)
            cached = cache.get(hash_key)
            if cached:
                self.runways, self.taxiways, self.pushback_ways = cached
                self.logger.debug("Done breaking links using cache")
                return

        # Retrieve all nodes and links
        all_nodes = self.spots + []

        for link in self.links:
            all_nodes.append(link.start)
            all_nodes.append(link.end)
            self.__add_break_node(link.start)
            self.__add_break_node(link.end)

        index = 0
        while index < len(all_nodes):
            index = self.__break_next_link(all_nodes, index)

        self.logger.info("Done breaking links")
        self.__get_break_nodes()

        # Stores the result into cache for future usages
        if cache_enabled:
            to_cache = [self.runways, self.taxiways, self.pushback_ways]
            cache.put(hash_key, to_cache)

    def __break_next_link(self, all_nodes, index):

        for i in range(index, len(all_nodes)):
            node = all_nodes[i]

            # TODO: Not splitting runways. Should take arrivals into consideration.

            # Taxiway
            for taxiway in self.taxiways:
                if taxiway.contains_node(node):
                    self.logger.info("Break found at %s on %s", node, taxiway)
                    self.__add_break_node(node)
                    self.taxiways.remove(taxiway)
                    self.taxiways += taxiway.break_at(node)
                    return i
l
            # Pushback ways
            for pushback_way in self.pushback_ways:
                if pushback_way.contains_node(node):
                    self.pushback_ways.remove(pushback_way)
                    self.pushback_ways += pushback_way.break_at(node)
                    self.logger.info("Break found at %s on %s",
                                     node, pushback_way)
                    self.__add_break_node(node)
                    return i

        return len(all_nodes)

    def __add_break_node(self, node):
        lat, lng = node.geo_pos["lat"], node.geo_pos["lng"]
        self.break_nodes.add(
            """
            <Placemark>
                <name>{lng},{lat}</name>
                <Point>
                  <coordinates>
                    {lng},{lat}
                  </coordinates>
                </Point>
            </Placemark>
            """.format(lat=lat, lng=lng))

    def __get_break_nodes(self):
        break_nodes_kml = """
        <?xml version="1.0" encoding="UTF-8"?>
        <kml xmlns="http://www.opengis.net/kml/2.2">
          <Document>
            <name>Break Nodes</name>
            <description/>
            <Folder>
              <name>Break Node (Debug)</name>
              {nodes}
            </Folder>
          </Document>
        </kml>
        """.format(nodes="".join(self.break_nodes))

        return break_nodes_kml

    def __repr__(self):
        return "<Surface>"

    def get_node(self, name):
        """Gets the node with its name and raises exception if no such node is
        found since we should always work on nodes that we know.
        """

        for gate in self.gates:
            if gate.name == name:
                return gate

        for spot in self.spots:
            if spot.name == name:
                return spot

        raise Exception("Getting an unknown node")

    def get_link(self, name):
        """Gets the link with its name and raises exception if no such link is
        found.
        """

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

    @property
    def links(self):
        """Returns all links."""
        return self.runways + self.taxiways + self.pushback_ways

    @property
    def nodes(self):
        """Returns all nodes."""
        return self.gates + self.spots

    def print_stats(self):
        """Prints the statistics of this airport surface."""
        self.logger.debug("%d gates, %d spots, %d runways, %d taxiways",
                          len(self.gates), len(self.spots), len(self.runways),
                          len(self.taxiways))

    def __getstate__(self):
        attrs = dict(self.__dict__)
        del attrs["logger"]
        return attrs

    def __setstate__(self, attrs):
        self.__dict__.update(attrs)

    def set_quiet(self, logger):
        """Sets the aircraft into quiet mode where less logs are printed."""
        self.logger = logger


class Gate(Node):
    """Extends `Node` class to represent a gate."""

    def __init__(self, name, geo_pos):
        Node.__init__(self, name, geo_pos)


class Spot(Node):
    """Extends `Node` class to represent a spot position."""

    def __init__(self, name, geo_pos):
        Node.__init__(self, name, geo_pos)


class RunwayNode(Node):
    """Extends `Node` class to represent a runway node."""

    def __init__(self, geo_pos):
        Node.__init__(self, "", geo_pos)


class Runway(Link):
    """Extends `Link` class to represent a runway."""

    def __init__(self, name, nodes):
        Link.__init__(self, name, nodes)

    def __repr__(self):
        return "<RUNWAY: %s>" % self.name


class Taxiway(Link):
    """Extends `Link` class to represent a taxiway."""

    def __init__(self, name, nodes):
        Link.__init__(self, name, nodes)

    def __repr__(self):
        return "<TAXIWAY: %s>" % self.name


class PushbackWay(Link):
    """Extends `Link` class to represent a pushback way."""

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
    def create(cls, dir_path):
        """Creates a new surface object given its source directory."""
        if not SurfaceFactory.__is_data_ready(dir_path):
            raise Exception("Surface data is not ready")
        with open(dir_path + "airport-metadata.json") as fin:
            airport_raw = json.load(fin)
        cls.logger = logging.getLogger(__name__)
        surface = Surface(airport_raw["center"], airport_raw["corners"],
                          dir_path + "airport.jpg")
        SurfaceFactory.__load_gates(surface, dir_path)
        SurfaceFactory.__load_spots(surface, dir_path)
        SurfaceFactory.__load_runway(surface, dir_path)
        SurfaceFactory.__load_taxiway(surface, dir_path)
        SurfaceFactory.__load_pushback_way(surface, dir_path)
        surface.break_links()
        return surface

    @classmethod
    def __is_data_ready(cls, dir_path):

        # Checks if the files exist
        for file_to_check in SurfaceFactory.FILES_TO_CHECK:
            file_path = dir_path + file_to_check
            if not os.path.exists(file_path):
                return False

        return True

    @classmethod
    def __load_gates(cls, surface, dir_path):
        surface.gates = SurfaceFactory.__retrieve_node("gates", dir_path)
        cls.logger.info("%s gates loaded", len(surface.gates))

    @classmethod
    def __load_spots(cls, surface, dir_path):
        surface.spots = SurfaceFactory.__retrieve_node("spots", dir_path)
        cls.logger.info("%s spots loaded", len(surface.spots))

    @classmethod
    def __retrieve_node(cls, type_name, dir_path):

        nodes = []

        with open(dir_path + type_name + ".json") as fin:
            nodes_raw = json.load(fin)

        for node_raw in nodes_raw:

            name = node_raw["name"]

            if type_name == "spots":
                nodes.append(
                    Spot(
                        name,
                        {"lat": node_raw["lat"], "lng": node_raw["lng"]}
                    )
                )
            elif type_name == "gates":
                nodes.append(
                    Gate(
                        name,
                        {"lat": node_raw["lat"], "lng": node_raw["lng"]}
                    )
                )
            else:
                raise Exception("Unknown node type")

        return nodes

    @classmethod
    def __load_runway(cls, surface, dir_path):
        surface.runways = SurfaceFactory.__retrive_link("runways", dir_path)
        cls.logger.info("%s runways loaded", len(surface.runways))

    @classmethod
    def __load_taxiway(cls, surface, dir_path):
        surface.taxiways = SurfaceFactory.__retrive_link("taxiways", dir_path)
        cls.logger.info("%s taxiways loaded", len(surface.taxiways))

    @classmethod
    def __load_pushback_way(cls, surface, dir_path):
        surface.pushback_ways = SurfaceFactory.__retrive_link("pushback_ways",
                                                              dir_path)
        cls.logger.info("%s pushback ways loaded", len(surface.pushback_ways))

    @classmethod
    def __retrive_link(cls, type_name, dir_path):

        links = []

        with open(dir_path + type_name + ".json") as fin:
            links_raw = json.load(fin)

        for link_raw in links_raw:

            name = link_raw["name"]

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
