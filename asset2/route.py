class Route:
    """
    Route represents a long path composed with a start node, an end node, and
    the links in between. A route can be imcompleted (start and end nodes are
    set but the links are being added incrementally), and we can call
    `is_completed` function to see if this route is connected from start to
    end.
    """

    INFINITE_DISTANCE = 1000000

    def __init__(self, start, end, links):

        self.links = []
        self.start = start
        self.end = end
        self.links.extend(links)

    def add_link(self, link):

        last_node = self.get_last_attempted_node()

        # If the last_node is not the same as the start of the new link, raise
        # exception
        if not last_node.is_close_to(link.start):
            Tracer()()
            raise Exception("New link start node doesn't match with the last " \
                            "node")
        self.links.append(link)

    def add_links(self, links):
        for link in links:
            self.add_link(link)

    """
    Gets the last node that we can reach from the start node. Returns None if
    there's no link in this route.
    """
    def get_last_attempted_node(self):
        if len(self.links) == 0:
            return self.start
        return self.links[len(self.links) - 1].end

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
        if not self.links[0].start.is_close_to(self.start):
            return False

        # If any two of the links are not connected, return false
        end_of_prev_link = None
        for link in self.links:
            if end_of_prev_link and \
               not end_of_prev_link.is_close_to(link.start):
                return False
            end_of_prev_link = link.end

        return end_of_prev_link.is_close_to(self.end)

    """
    Gets the whole distance of this route, raises exception if the route is not
    completed yet.
    """
    @property
    def distance(self):
        if not self.is_completed():
            return self.INFINITE_DISTANCE
        distance = 0
        for link in self.links:
            distance += link.length
        return distance

    """
    Removes all the stored links.
    """
    def reset_links(self):
        self.links = []

    def __repr__(self):
        return "<Route: %s - %s>" % (self.start, self.end)

    @property
    def description(self):
        s = "distance: %f\n" % self.distance
        for link in self.links:
            s += "> link: %s to %s, distance: %f\n" % (link.start, link.end,
                                                       link.length)
        return s

# TODO
class Itinerary:

    def __init__(self, route, expected_start_time):
        self.route = route
        self.expected_start_time = expected_start_time

    @property
    def distance_left(self):
        return 0

    def get_estimated_finish_time(self, v):
        return 0

    def move_distance_feet(self, distance):
        # self.current_location += distance
        return self.current_location

    def is_completed(self):
        return self.current_location.is_close_to(self.route.end)
