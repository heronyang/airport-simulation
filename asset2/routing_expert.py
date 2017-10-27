import logging
import cache

from link import Link
from route import Route

class RoutingExpert:

    def __init__(self, links, nodes):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        self.routing_table = {}

        # Adds the two ends of a links as a node as well
        for link in links:
            nodes.append(link.start)
            nodes.append(link.end)

        # Saves all the links and nodes
        self.links = links
        self.nodes = nodes

        # Builds or loads the routing table from cache
        self.build_or_load_routes()

    def build_or_load_routes(self):

        hash_key = cache.hash(self.links, self.nodes)
        cached = cache.get(hash_key)

        if cached:
            self.routing_table = cached
            self.logger.debug("Cached routing table is loaded")
        else:
            # Builds the routes
            self.build_routes()
            cache.put(hash_key, self.routing_table)

    def build_routes(self):

        self.logger.debug("Starts building routes, # nodes: %d # links: %d" %
                          (len(self.nodes), len(self.links)))
        self.init_routing_table()

        # Step 1: Links two nodes with really short distance (using
        # is_close_to method)
        self.logger.debug("Starts linking close nodes")
        self.link_close_nodes()

        # Step 2: Links the start and end node of the links
        self.logger.debug("Starts linking existing links")
        self.link_existing_links()

        # Step 3: Applies Floyd–Warshall algorithm to get shortest routes for
        # all node pairs
        self.logger.debug("Starts floyd-warshall for finding shortest routes")
        self.finds_shortest_route()

        # Prints result
        self.print_route()

    def init_routing_table(self):

        # Initializes the routing table
        for start in self.nodes:
            self.routing_table[start] = {}
            for end in self.nodes:
                if (start == end):
                    self.routing_table[start][end] = None
                else:
                    self.routing_table[start][end] = Route(start, end, [])

    def link_close_nodes(self):

        for start in self.nodes:
            for end in self.nodes:
                if start != end and start.is_close_to(end):
                    link = Link(0, "CLOSE_NODE_LINK", [start, end])
                    self.routing_table[start][end].add_link(link)
                    if not self.routing_table[start][end].is_completed():
                        raise Exception("Unable to link two close nodes")

    def link_existing_links(self):

        for link in self.links:
            start = link.start
            end = link.end

            self.routing_table[start][end].add_link(link)
            self.routing_table[end][start].add_link(link.reverse)

            if not (self.routing_table[start][end].is_completed() and 
                    self.routing_table[end][start].is_completed()):
                raise Exception("Unable to link two ends of a link from %s" +\
                                " to %s" % (start, end))

    def finds_shortest_route(self):

        # Floyd-Warshall
        for k in self.nodes:
            for i in self.nodes:
                for j in self.nodes:

                    r_ij = self.routing_table[i][j]
                    r_ik = self.routing_table[i][k]
                    r_kj = self.routing_table[k][j]

                    # Ignores the nodes with no route in between
                    if r_ik is None or r_kj is None or r_ij is None:
                        continue

                    # Ignores the cases where i -> k or k -> j is not connected
                    if not r_ik.is_completed() or not r_kj.is_completed():
                        continue

                    # Updates the i -> j route if i -> k -> j is shorter
                    if r_ik.distance + r_kj.distance < r_ij.distance:
                        r_ij.reset_links()
                        r_ij.add_links(r_ik.links)
                        r_ij.add_links(r_kj.links)

    def print_route(self):

        for start in self.nodes:
            for end in self.nodes:
                self.logger.debug("[%s - %s]" % (start, end))
                route = self.routing_table[start][end] 
                if (route):
                    self.logger.debug(route.description)
                else:
                    self.logger.debug("No Route")

    """
    Gets the shortest route by given start and end node.
    """
    def get_shortest_route(self, start, end):
        if (not start in self.routing_table) or (not end in self.routing_table[start]):
            return None
        return self.routing_table[start][end]
