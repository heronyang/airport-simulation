"""Class file for `RoutingExpert`."""
import logging
import cache

from link import Link
from route import Route
from surface import Runway, Spot, Gate, RunwayNode


class RoutingExpert:
    """`RoutingExpert` contains the knownledge of providing routes between any
    two nodes in the airport surfact. It provides `get_shortest_route`
    interface for the scheduler to use for providing itineraries. The routes
    are precomputed and cached per airport.
    """

    def __init__(self, links, nodes, enable_cache):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        self.depart_routing_table = {}
        self.arrival_routing_table = {}

        # Adds the two ends of a links as a node as well
        for link in links:
            nodes.append(link.start)
            nodes.append(link.end)

        # Saves all the links and nodes
        self.links = links
        self.nodes = nodes
        self.runway_nodes = list(map(lambda l: l.start, list(filter(lambda l: type(l) == Runway, self.links))))
        self.spot_nodes = list(filter(lambda l: type(l) == Spot, self.nodes))
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
            (self.depart_routing_table, self.arrival_routing_table) = cached
            self.logger.debug("Cached routing table is loaded")
        else:
            # Builds the routes
            self.__build_routes()
            cache.put(hash_key, (self.depart_routing_table, self.arrival_routing_table))

    def __build_routes(self):
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
        self.depart_routing_table = self.__finds_shortest_route_spfa(self.runway_nodes)
        self.arrival_routing_table = self.__finds_shortest_route_spfa(self.spot_nodes)

        # Prints result
        self.print_depart_route(self.depart_routing_table)
        # TODO: print arrival route
        # self.print_route(self.arrival_routing_table)

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

    def __finds_shortest_route_spfa(self, dest_nodes):
        routing_table = {}
        for r in dest_nodes:
            routing_table[r] = {}

            for n in self.nodes:
                if n == r:
                    continue
                routing_table[r][n] = Route(n, r, [])

            candidates = CandidateNeighbors(r)

            while candidates.length:
                u = candidates.pop()

                for v in self.adjacency_map[u]:
                    new_distance = routing_table[r][u].distance + self.adjacency_map[u][v].length \
                        if r != u else self.adjacency_map[u][v].length
                    old_distance = routing_table[r][v].distance if r != v else 0
                    if new_distance < old_distance:
                        routing_table[r][v].reset_links()
                        routing_table[r][v].add_link(self.adjacency_map[v][u])
                        if r != u:
                            routing_table[r][v].add_links(routing_table[r][u].links)

                        self.logger.debug("%s -> %s -> %s is shorter than "
                                          "%s -> %s", v, u, r, v, r)

                        if not candidates.has(v):
                            candidates.push(v)
                            candidates.re_order(routing_table[r])

            for node in self.nodes:
                # r is in the routing table; some nodes could be unreachable
                if node not in routing_table[r] or not len(routing_table[r][node].links):
                    continue
                if not routing_table[r][node].is_completed:
                    raise Exception("Incomplete route found.")
        return routing_table

    def print_depart_route(self, routing_table):
        """Prints all the routes into STDOUT."""

        for start in self.runway_nodes:
            for end in self.nodes:
                if start == end:
                    continue
                self.logger.debug("[%s - %s]", end, start)
                route = routing_table[start][end]
                if route:
                    self.logger.debug(route.description)
                else:
                    self.logger.debug("No Route")

    def get_shortest_route(self, start, end):
        """
        Gets the shortest route by given start and end node.
        For departure, end node must be a runway node.
        For arrival, end node must be a gate node.
        Assume the arrival start point is outside of Spot.
        """
        # GEO_MIDDLE_NORTH = {"lat": 37.122000, "lng": -122.079057}
        # SP1 = Spot("SP1", GEO_MIDDLE_NORTH)
        if end in self.runway_nodes:
            if start not in self.depart_routing_table[end]:
                return None
            return self.depart_routing_table[end][start]

        if type(end) == Gate:
            spot = end.get_spots()
            # spot = SP1
            node_to_spot = self.arrival_routing_table[spot][start]
            spot_to_gate = self.arrival_routing_table[spot][end]
            spot_to_gate.reverse()
            result = Route(start, end, [])
            result.add_links(node_to_spot.get_links())
            result.add_links(spot_to_gate.get_links())
            return result

        raise Exception("End node is not a runway node nor a gate node.")

    def __getstate__(self):
        attrs = dict(self.__dict__)
        del attrs["logger"]
        return attrs

    def __setstate__(self, attrs):
        self.__dict__.update(attrs)

    def set_quiet(self, logger):
        """Sets this object into quiet mode where less logs are printed."""
        self.logger = logger


class CandidateNeighbor:
    def __init__(self, node):
        self.node = node
        self.next = None
        self.prev = None


class CandidateNeighbors:
    def __init__(self, node):
        self.tail = self.head = CandidateNeighbor(node)
        self.set = {node}

    def pop(self):
        if not self.head:
            return None

        node, self.head = self.head.node, self.head.next
        if self.head:
            self.head.prev = None
        else:
            self.tail = None

        self.set.remove(node)

        return node

    def push(self, node):
        self.set.add(node)

        if self.tail:
            self.tail.next = CandidateNeighbor(node)
            self.tail.next.prev = self.tail
            self.tail = self.tail.next
        else:
            self.tail = self.head = CandidateNeighbor(node)

    def has(self, node):
        return node in self.set

    @property
    def length(self):
        return len(self.set)

    def re_order(self, routes):
        if routes[self.tail.node].distance < routes[self.head.node].distance:
            front, self.head = self.head.node, self.head.next
            if self.head:
                self.head.prev = None

            self.push(front)
