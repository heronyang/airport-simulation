from geopy.distance import vincenty

class Node:

    def __init__(self, index, geo_pos):

        if not self.__is_valid_geo_pos(geo_pos):
            raise Exception("Invalid geo position")

        self.__index = index
        self.__geo_pos = geo_pos

    def __is_valid_geo_pos(self, geo_pos):
        lat = geo_pos["lat"]
        lng = geo_pos["lng"]
        if lat < -90 or lat > 90:
            return False
        if lng < -180 or lng > 180:
            return False
        return True

    def get_index(self):
        return self.__index
    
    def get_geo_pos(self):
        return self.__geo_pos

    # Returns the distance from this node to another in feets
    def get_distance_to(self, node):
        sp = self.get_geo_pos()
        ss = node.get_geo_pos()
        distance = vincenty(
            (sp["lat"], sp["lng"]),
            (ss["lat"], ss["lng"]),
        )
        return distance.feet
