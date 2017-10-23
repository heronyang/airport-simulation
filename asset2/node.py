from utils import is_valid_geo_pos
from geopy.distance import vincenty

class Node:

    CLOSE_NODE_THRESHOLD_FEET = 30

    def __init__(self, index, name, geo_pos):

        if not is_valid_geo_pos(geo_pos):
            raise Exception("Invalid geo position")

        self.name = name
        self.index = index
        self.geo_pos = geo_pos

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
        return distance_feet < self.CLOSE_NODE_THRESHOLD_FEET

    def __repr__(self):
        return "<Node: %s>" % self.name
