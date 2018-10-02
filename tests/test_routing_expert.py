#!/usr/bin/env python

from node import Node
from link import Link
from routing_expert import RoutingExpert
from airport import Airport
from scenario import Scenario
from surface import RunwayNode, Runway

import sys
import unittest

sys.path.append('..')


class TestRoutingExpert(unittest.TestCase):
    """
    G1 is linked to S1 via L1 and L2. L2 is longer than L1.
    """
    GEO_WEST = {"lat": 37.422000, "lng": -122.084057}
    GEO_EAST = {"lat": 37.422000, "lng": -122.074057}
    GEO_MIDDLE_NORTH = {"lat": 37.122000, "lng": -122.079057}
    GEO_MIDDLE_SOUTH = {"lat": 47.722000, "lng": -122.079057}

    G1 = Node("G1", GEO_WEST)
    S1 = RunwayNode(GEO_EAST)
    L1 = Link("L1", [
        Node("L1_start", GEO_WEST),
        Node("L1_middle", GEO_MIDDLE_NORTH),
        Node("L1_end", GEO_EAST)
    ])
    L2 = Link("L2", [
        Node("L2_start", GEO_WEST),
        Node("L2_middle", GEO_MIDDLE_SOUTH),
        Node("L2_end", GEO_EAST)
    ])

    L3 = Runway("Runway", [
        S1, S1
    ])

    links = [L1, L2, L3]
    nodes = [G1, S1]

    def test_overlapped_link(self):
        routing_expert = RoutingExpert(self.links, self.nodes, False)
        route = routing_expert.get_shortest_route(self.G1, self.S1)

        # Checks if the shortest route uses L1
        self.assertEqual(route.links[1], self.L1)

        # Checks if the shortest distance is expected
        self.assertAlmostEqual(route.distance, 218489.353890, 5)

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
        self.airport = Airport.create(airport_code)

        # Sets up the scenario
        self.scenario = Scenario.create(airport_code,
                                        self.airport.surface)

        links = self.airport.surface.links
        nodes = self.airport.surface.nodes

        # Sets up the routing expert monitoring the airport surface
        routing_expert = RoutingExpert(links, nodes, False)

        routeG3toR1 = routing_expert.get_shortest_route(nodes[2],
                                                        links[0].start)

        self.assertEqual(len(routeG3toR1.nodes), 8)
        self.assertAlmostEqual(routeG3toR1.distance, 1352.6500035604972, 5)

    def test_sfo_terminal_2_closest(self):
        airport_code = "sfo-terminal-2"

        # Sets up the airport
        self.airport = Airport.create(airport_code)

        # Sets up the scenario
        self.scenario = Scenario.create(airport_code,
                                        self.airport.surface)

        links = self.airport.surface.links
        nodes = self.airport.surface.nodes

        routing_expert = RoutingExpert(links, nodes, True)
        runway_start = self.airport.surface.get_link("10R/28L").start

        # Checks the gate that is near to the runway (G58B)
        gate_58B = self.airport.surface.get_node("58B")
        routeG58Bto10R = \
            routing_expert.get_shortest_route(gate_58B, runway_start)

        self.assertAlmostEqual(routeG58Bto10R.distance, 8198.5613013809, 5)
        self.assertEqual(len(routeG58Bto10R.nodes), 32)
        self.assertEqual(len(routeG58Bto10R.links), 31)

    def test_sfo_terminal_2_furthest(self):
        airport_code = "sfo-terminal-2"

        # Sets up the airport
        self.airport = Airport.create(airport_code)

        # Sets up the scenario
        self.scenario = Scenario.create(airport_code,
                                        self.airport.surface)

        links = self.airport.surface.links
        nodes = self.airport.surface.nodes

        routing_expert = RoutingExpert(links, nodes, True)
        runway_start = self.airport.surface.get_link("10R/28L").start

        # Checks the gate that is far from the runway (G53)
        gate_53 = self.airport.surface.get_node("53")

        routeG53to10R = \
            routing_expert.get_shortest_route(gate_53, runway_start)
        self.assertAlmostEqual(routeG53to10R.distance, 10014.749180929799, 5)
        self.assertEqual(len(routeG53to10R.nodes), 39)
        self.assertEqual(len(routeG53to10R.links), 38)

    def test_sfo_terminal_2_all(self):
        airport_code = "sfo-terminal-2"

        # Sets up the airport
        self.airport = Airport.create(airport_code)

        # Sets up the scenario
        self.scenario = Scenario.create(airport_code,
                                        self.airport.surface)

        links = self.airport.surface.links
        nodes = self.airport.surface.nodes

        routing_expert = RoutingExpert(links, nodes, True)
        runway_start = self.airport.surface.get_link("10R/28L").start

        # Checks the gate that is far from the runway (G53)
        gate_names = ["50", "55", "53", "52", "54A", "51A", "51B", "54B",
                      "56B", "56A", "57", "59", "58B", "58A"]
        for gate_name in gate_names:
            gate = self.airport.surface.get_node(gate_name)
            route = routing_expert.get_shortest_route(gate, runway_start)
            # Make sure they all have a route to go to the runway
            self.assertTrue(len(route.nodes) >= 2)
            self.assertTrue(len(route.links) >= 1)
            self.assertTrue(route.distance > 0.0)


if __name__ == '__main__':
    unittest.main()
