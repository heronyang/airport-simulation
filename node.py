from utils import is_valid_geo_pos, str2sha1
from geopy.distance import vincenty
from utils import random_string
from config import Config
from id_generator import get_new_node_id


class Node:

    def __init__(self, name, geo_pos):

        if not is_valid_geo_pos(geo_pos):
            raise Exception("Invalid geo position")

        if name is None or len(name) == 0:
            name = "n-id-" + str(get_new_node_id())

        self.name = name
        self.geo_pos = geo_pos
        self.hash = str2sha1("%s#%.5f#%.5f" %
                             (name, geo_pos["lat"], geo_pos["lng"]))

    """
    Returns the distance from this node to another in feets
    """
    def get_distance_to(self, node):
        sp = self.geo_pos
        ss = node.geo_pos
        distance = vincenty(
            (sp["lat"], sp["lng"]),
            (ss["lat"], ss["lng"]),
        )
        return distance.feet

    """
    If the node is in CLOSE_NODE_THRESHOLD_FEET feets from the current node, we
    take them as the same node
    """
    def is_close_to(self, node):
        distance_feet = self.get_distance_to(node)
        threshold = Config.params["simulation"]["close_node_threshold"]
        return distance_feet < threshold

    """
    Override functions used for hash and comparisons so that we will able to
    match nodes after the objects had been reconstructed or copied.
    """
    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not(self == other)

    def __repr__(self):
        return "<Node: %s|%f,%f>" % ((self.name if self.name else "NULL"),
                                     self.geo_pos["lat"],
                                     self.geo_pos["lng"])

def get_middle_node(n1, n2, ratio=None):

    if not ratio:

        return Node(
            "MIDDLE_NODE", {
                "lat": (n1.geo_pos["lat"] + n2.geo_pos["lat"]) / 2,
                "lng": (n1.geo_pos["lng"] + n2.geo_pos["lng"]) / 2
            }
        )

    lat1, lat2 = n1.geo_pos["lat"], n2.geo_pos["lat"]
    lng1, lng2 = n1.geo_pos["lng"], n2.geo_pos["lng"]

    return Node(
        "RATIO_MIDDLE_NODE", {
            "lat": lat1 + (lat2 - lat1) * ratio,
            "lng": lng1 + (lng2 - lng1) * ratio
        }
    )
