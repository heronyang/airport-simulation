from utils import is_valid_geo_pos
from geopy.distance import vincenty

class Node:

    SAME_NODE_THRESHOLD_FEET = 10

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
    If the node is in SAME_NODE_THRESHOLD_FEET feets from the current node, we
    take them as the same node
    """
    def is_same(self, node):
        distance_feet = self.get_distance_to(node)
        return distance_feet < self.SAME_NODE_THRESHOLD_FEET
