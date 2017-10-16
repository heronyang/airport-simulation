class Route:
    """
    Route represents a long path composed with a start node, an end node, and
    the links in between. A route can be imcompleted (start and end nodes are
    set but the links are being added incrementally), and we can call
    `is_completed` function to see if this route is connected from start to
    end.
    """

    links = []

    def __init__(self, start, end, links):
        self.start = start
        self.end = end
        self.links.extend(links)

    def add_link(self, link):

        last_node = self.get_last()

        # If the last_node is not the same as the start of the new link, raise
        # exception
        if last_node and not last_node.is_same(link.get_start):
            raise Exception("New link start node doesn't match with the last " \
                            "node")
        self.links.append(link)

    """
    Gets the last node that we can reach from the start node. Returns None if
    there's no link in this route.
    """
    def get_last_attempted_node(self):
        if len(self.links) == 0:
            return None
        return self.links[len(self.links) - 1].get_last()

    """
    Returns true if the whole route is connected properly with different links
    from start to end.
    """
    def is_completed(self):

        # If this route contains no link return false
        if len(self.links) < 1:
            return False

        # If this route start node is not the start of the first link, return
        # false
        if not self.links[0].get_start.is_same(self.start):
            return False

        # If any two of the links are not connected, return false
        end_of_prev_link = None
        for link in self.links:
            if end_of_prev_link and \
               not end_of_prev_link.is_same(link.get_start()):
                return False
            end_of_prev_link = link.get_end()

        return end_of_prev_link.is_same(self.end)

# TODO
class Itinerary:

    def __init__(self, route, expected_start_time):
        self.current_location = route.start
        self.route = route
        self.expected_start_time = expected_start_time

    def get_distance_left(self):
        return 0

    def get_estimated_finish_time(self, v):
        return 0

    def move_distance_feet(self, distance):
        # self.current_location += distance
        return self.current_location

    def is_completed(self):
        return self.current_location.is_same(self.route.end)

# TODO
class RouteExpert:

    def __init__(self, nodes, links):
        pass

    def get_shortest_route(self, start, end):
        return Route(start, end, [])
