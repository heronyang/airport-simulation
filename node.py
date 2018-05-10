"""Class file for `Node`."""
from utils import is_valid_geo_pos, str2sha1
from geopy.distance import vincenty
from config import Config
from id_generator import get_new_node_id


class Node:
    """`Node` is one of the most important class in our link-node model where
    is represents a physical node in the aircraft surface.
    """

    def __init__(self, name, geo_pos):

        if not is_valid_geo_pos(geo_pos):
            raise Exception("Invalid geo position")

        if name is None or len(name) == 0:
            name = "n-id-" + str(get_new_node_id())

        self.name = name
        self.geo_pos = geo_pos
        self.hash = str2sha1("%s#%.5f#%.5f" %
                             (name, geo_pos["lat"], geo_pos["lng"]))

    def get_distance_to(self, node):
        """Returns the distance from this node to another in feets."""
        this_node = self.geo_pos
        another_node = node.geo_pos
        distance = vincenty(
            (this_node["lat"], this_node["lng"]),
            (another_node["lat"], another_node["lng"]),
        )
        return round(distance.feet, Config.DECIMAL_ROUND)

    def is_close_to(self, node):
        """If the node is in CLOSE_NODE_THRESHOLD_FEET feets from the current
        node, we take them as the same node.
        """
        distance_feet = self.get_distance_to(node)
        threshold = Config.params["simulation"]["close_node_threshold"]
        return distance_feet < threshold

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "<Node: %s|%f,%f>" % ((self.name if self.name else "NULL"),
                                     self.geo_pos["lat"],
                                     self.geo_pos["lng"])


def get_middle_node(src, dst, ratio=None):
    """Gets the middle node m between two nodes with a given `ratio` where
    |src-m| / |dst-src| is `ratio`. If the `ratio` is None, 0.5 is used as the
    ratio.
    """

    if ratio is None:
        return Node(
            "MIDDLE_NODE", {
                "lat": (src.geo_pos["lat"] + dst.geo_pos["lat"]) / 2,
                "lng": (src.geo_pos["lng"] + dst.geo_pos["lng"]) / 2
            }
        )

    lat1, lat2 = src.geo_pos["lat"], dst.geo_pos["lat"]
    lng1, lng2 = src.geo_pos["lng"], dst.geo_pos["lng"]

    return Node(
        "RATIO_MIDDLE_NODE", {
            "lat": lat1 + (lat2 - lat1) * ratio,
            "lng": lng1 + (lng2 - lng1) * ratio
        }
    )
