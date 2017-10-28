from utils import is_valid_geo_pos
from geopy.distance import vincenty
from config import Config

class Node:

    def __init__(self, index, name, geo_pos):

        if not is_valid_geo_pos(geo_pos):
            raise Exception("Invalid geo position")

        self.index = index
        self.name = name
        self.geo_pos = geo_pos
        self.hash = hash("%s#%s#%s" % (index, name, geo_pos))

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
        return distance_feet < Config.CLOSE_NODE_THRESHOLD_FEET

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
