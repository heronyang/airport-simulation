from link import Link
from config import Config


class Route:
    """
    Route represents a long path composed with a start node, an end node, and
    the links in between. A route can be imcompleted (start and end nodes are
    set but the links are being added incrementally), and we can call
    `is_completed` function to see if this route is connected from start to
    end.
    """

    def __init__(self, start, end, links):

        self.links = []
        self.start = start
        self.end = end
        self.links.extend(links)
        self.__distance = None  # distance is calculated lazily
        self.__is_completed = None  # is_completed is calculated lazily
        self.__nodes = []   # nodes are calculated lazily

    def update_link(self, link):
        self.reset_links()
        self.__add_link(link)

    def add_links(self, links):
        for link in links:
            self.__add_link(link)

    def __add_link(self, link):

        last_node = self.last_attempted_node

        # If the last_node is not the same as the start of the new link, raise
        # exception
        if not last_node.is_close_to(link.start):
            raise Exception("New link start node doesn't match with the "
                            "last node")
        self.links.append(link)
        self.reset_cache()

    def prepend(self, node):
        if node == self.start:
            return
        link = Link("PREPEND_LINK", [node, self.start])
        self.links.insert(0, link)
        self.start = node
        self.reset_cache()

    @property
    def nodes(self):
        """
        Returns all nodes among this route.
        """
        if len(self.__nodes) > 0:
            return self.__nodes

        nodes = [self.start]
        for link in self.links[1:]:
            nodes.append(link.start)
        nodes.append(self.end)

        self.__nodes = nodes
        return self.__nodes

    """
    Gets the last node that we can reach from the start node. Returns None if
    there's no link in this route.
    """
    @property
    def last_attempted_node(self):
        if len(self.links) == 0:
            return self.start
        return self.links[len(self.links) - 1].end

    """
    Returns true if the whole route is connected properly with different links
    from start to end.
    """
    @property
    def is_completed(self):

        if self.__is_completed:
            return self.__is_completed

        self.__is_completed = self.__get_is_completed()
        return self.__is_completed

    def __get_is_completed(self):

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
        if self.__distance:
            return self.__distance
        self.__distance = self.__get_distance()
        return self.__distance

    def __get_distance(self):
        if not self.is_completed:
            return float("Inf")
        distance = 0
        for link in self.links:
            distance += link.length
        return distance


    """
    Removes all the stored links.
    """
    def reset_links(self):
        self.links = []
        self.reset_cache()

    def reset_cache(self):
        self.__distance = None
        self.__is_completed = None
        self.__nodes = []

    def __repr__(self):
        return "<Route: %s - %s>" % (self.start, self.end)

    @property
    def description(self):
        s = "distance: %f\n" % self.distance
        for link in self.links:
            s += "> link: %s to %s, distance: %f\n" % \
                    (link.start, link.end, link.length)
        return s
