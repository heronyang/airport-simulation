#!/usr/bin/env python

import sys
import unittest
sys.path.append('..')

from node import Node
from link import Link
from routing_expert import RoutingExpert
from airport import AirportFactory
from scenario import ScenarioFactory

class TestRoutingExpert(unittest.TestCase):

    """
    G1 is linked to S1 via L1 and L2. L2 is longer than L1.
    """
    GEO_WEST = {"lat": 37.422000, "lng": -122.084057}
    GEO_EAST = {"lat": 37.422000, "lng": -122.074057}
    GEO_MIDDLE_NORTH = {"lat": 37.122000, "lng": -122.079057}
    GEO_MIDDLE_SOUTH = {"lat": 47.722000, "lng": -122.079057}

    G1 = Node(0, "G1", GEO_WEST)
    S1 = Node(0, "S1", GEO_EAST)
    L1 = Link(0, "L1", [
        Node(0, "start", GEO_WEST),
        Node(0, "L1_middle", GEO_MIDDLE_NORTH),
        Node(0, "end", GEO_EAST)
    ])
    L2 = Link(0, "L2", [
        Node(0, "start", GEO_WEST),
        Node(0, "L2_middle", GEO_MIDDLE_SOUTH),
        Node(0, "end", GEO_EAST)
    ])

    links = [L1, L2]
    nodes = [G1, S1]

    def test_overlapped_link(self):

        routing_expert = RoutingExpert(self.links, self.nodes, False)
        route = routing_expert.get_shortest_route(self.G1, self.S1)

        # Checks if the shortest route uses L1
        self.assertEqual(route.links[1], self.L1)

        # Checks if the shortest distance is expected
        self.assertAlmostEqual(route.distance, 218489.353890, 6)

    def test_cache(self):

        # Try cache so we starts routing expert twice
        RoutingExpert(self.links, self.nodes, True)
        routing_expert = RoutingExpert(self.links, self.nodes, True)

        route = routing_expert.get_shortest_route(self.G1, self.S1)

        # Checks if the shortest route uses L1
        self.assertEqual(route.links[1], self.L1)

        # Checks if the shortest distance is expected
        self.assertAlmostEqual(route.distance, 218489.353890, 6)

    def test_simple_data(self):

        airport_code = "simple"

        # Sets up the airport
        self.airport = AirportFactory.create(airport_code)

        # Sets up the scenario
        self.scenario = ScenarioFactory.create(airport_code,
                                               self.airport.surface)

        links = self.airport.surface.links
        nodes = self.airport.surface.nodes

        # Sets up the routing expert monitoring the airport surface
        self.routing_expert = RoutingExpert(links, nodes, True)

        routeG3toR1 = self.routing_expert.get_shortest_route(nodes[2],
                                                             links[0].start)

if __name__ == '__main__':
	unittest.main()
