#!/usr/bin/env python

import sys
import unittest
sys.path.append('..')

from node import Node
from link import Link
from routing_expert import RoutingExpert
from utils import new_hash

class TestRoutingExpert(unittest.TestCase):

    def test_basic(self):
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
            Node(0, "L1_start", GEO_WEST),
            Node(0, "L1_middle", GEO_MIDDLE_NORTH),
            Node(0, "L1_end", GEO_EAST)
        ])
        L2 = Link(0, "L2", [
            Node(0, "L2_start", GEO_WEST),
            Node(0, "L2_middle", GEO_MIDDLE_SOUTH),
            Node(0, "L2_end", GEO_EAST)
        ])

        links = [L1, L2]
        nodes = [G1, S1]
        routing_expert = RoutingExpert(links, nodes, False)

        route = routing_expert.get_shortest_route(G1, S1)

        # Checks if the shortest route uses L1
        self.assertEqual(route.links[1], L1)

        # Checks if the shortest distance is expected
        self.assertAlmostEqual(route.distance, 218489.353890, 6)

    def test_overlapped_link(self):
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
        routing_expert = RoutingExpert(links, nodes, False)

        route = routing_expert.get_shortest_route(G1, S1)

        # Checks if the shortest route uses L1
        self.assertEqual(route.links[1], L1)

        # Checks if the shortest distance is expected
        self.assertAlmostEqual(route.distance, 218489.353890, 6)

if __name__ == '__main__':
	unittest.main()
