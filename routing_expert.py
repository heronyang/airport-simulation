"""Class file for `RoutingExpert`."""
import logging
import cache

from link import Link
from route import Route
from surface import Runway


class RoutingExpert:
    """`RoutingExpert` contains the knownledge of providing routes between any
    two nodes in the airport surfact. It provides `get_shortest_route`
    interface for the scheduler to use for providing itineraries. The routes
    are precomputed and cached per airport.
    """

    def __init__(self, links, nodes, enable_cache):

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
        self.runway_nodes = list(map(lambda l: l.start, list(filter(lambda l: type(l) == Runway, self.links))))
        self.logger.info("%d links and %d nodes are loaded",
                         len(self.links), len(self.nodes))

        # Builds or loads the routing table from cache
        if enable_cache:
            self.__build_or_load_routes()
        else:
            self.__build_routes()

    def __build_or_load_routes(self):

        hash_key = cache.get_hash(self.links, self.nodes)
        cached = cache.get(hash_key)

        if cached:
            self.routing_table = cached
            self.logger.debug("Cached routing table is loaded")
        else:
            # Builds the routes
            self.__build_routes()
            cache.put(hash_key, self.routing_table)
            exit(0)  # TODO: debug

    def __build_routes(self):
        import time  # TODO: debug
        start = time.time()  # TODO: debug

        self.logger.debug("Starts building routes, # nodes: %d # links: %d",
                          len(self.nodes), len(self.links))
        self.__init_adjacent_map()

        # Step 1: Links two nodes with really short distance (using
        # is_close_to method)
        self.logger.debug("Starts linking close nodes")
        self.__link_close_nodes()

        # Step 2: Links the start and end node of the links
        self.logger.debug("Starts linking existing links")
        self.__link_existing_links()

        # Step 3: Applies SPFA to get shortest routes for all node pairs
        self.logger.debug("Starts SPFA for finding shortest routes")
        self.__finds_shortest_route_spfa()

        # Prints result
        self.print_route()  # TODO: debug

        end = time.time()  # TODO: debug
        print("Time elapsed:", end - start)  # TODO: debug

    def __init_adjacent_map(self):
        # Initializes the adjacency map
        # self.adjacency_map[src][dst] = link
        self.adjacency_map = {}

        for node in self.nodes:
            self.adjacency_map[node] = {}

    def __link_close_nodes(self):
        counter = 0

        for start in self.nodes:
            for end in self.nodes:
                if start != end and start.is_close_to(end):
                    link = Link("CLOSE_NODE_LINK", [start, end])
                    self.adjacency_map[start][end] = link
                    self.logger.debug("%s and %s are close node", start, end)
                    counter += 1

        self.logger.debug("Adds %d links for close nodes", counter)

    def __link_existing_links(self):

        for link in self.links:
            start = link.start
            end = link.end

            # If there's already a link exists, store the shortest one
            if end in self.adjacency_map[start] and self.adjacency_map[start][end].length < link.length:
                continue
            else:
                self.adjacency_map[start][end] = link
                self.adjacency_map[end][start] = link.reverse

    def __finds_shortest_route_spfa(self):
        for r in self.runway_nodes:
            self.routing_table[r] = {}

            for n in self.nodes:
                if n == r:
                    continue
                self.routing_table[r][n] = Route(n, r, [])

            queue = [r]

            while queue:
                u = queue.pop(0)
                for v in self.adjacency_map[u]:
                    new_distance = self.routing_table[r][u].distance + self.adjacency_map[u][v].length \
                        if r != u else self.adjacency_map[u][v].length
                    old_distance = self.routing_table[r][v].distance if r != v else 0
                    if new_distance < old_distance:
                        self.routing_table[r][v].reset_links()
                        self.routing_table[r][v].add_link(self.adjacency_map[v][u])
                        if r != u:
                            self.routing_table[r][v].add_links(self.routing_table[r][u].links)

                        self.logger.debug("%s -> %s -> %s is shorter than "
                                          "%s -> %s", v, u, r, v, r)

                        if v not in queue:
                            queue.append(v)

            for node in self.nodes:
                # r is in the routing table; some nodes could be unreachable
                if node not in self.routing_table[r] or not len(self.routing_table[r][node].links):
                    continue
                if not self.routing_table[r][node].is_completed:
                    raise Exception("Incomplete route found.")

    def print_route(self):
        """Prints all the routes into STDOUT."""

        for start in self.runway_nodes:
            for end in self.nodes:
                if start == end:
                    continue
                self.logger.debug("[%s - %s]", end, start)
                route = self.routing_table[start][end]
                if route:
                    self.logger.debug(route.description)
                else:
                    self.logger.debug("No Route")

    def get_shortest_route(self, start, end):
        """
        Gets the shortest route by given start and end node.
        end node must be a runway node
        """
        if end not in self.runway_nodes:
            raise Exception("End node is not a runway node.")
        if start not in self.routing_table[end]:
            return None
        return self.routing_table[end][start]

    def __getstate__(self):
        attrs = dict(self.__dict__)
        del attrs["logger"]
        return attrs

    def __setstate__(self, attrs):
        self.__dict__.update(attrs)

    def set_quiet(self, logger):
        """Sets this object into quiet mode where less logs are printed."""
        self.logger = logger
