#!/usr/bin/env python3

from node import Node
from aircraft import Aircraft, State
from itinerary import Itinerary
from copy import deepcopy
from config import Config

import sys
import unittest
sys.path.append('..')


class TestAircraft(unittest.TestCase):

    Config.params["simulator"]["test_mode"] = True

    # Generates a itinerary_template
    n1 = Node("N1", {"lat": 47.722000, "lng": -122.079057})
    n2 = Node("N2", {"lat": 47.822000, "lng": -122.079057})
    n3 = Node("N3", {"lat": 47.922000, "lng": -122.079057})

    m1 = Node("M1", {"lat": 47.772000, "lng": -122.079057})
    m2 = Node("M2", {"lat": 47.872000, "lng": -122.079057})

    m = Node("M", {"lat": 47.755333, "lng": -122.079057})

    itinerary_template = Itinerary([n1, n2, n3])

    def test_init(self):

        aircraft = Aircraft("F1", "M1", self.n1, State.unknown)
        aircraft.set_location(self.n1)
        self.assertEqual(aircraft.location, self.n1)

    def test_tick(self):

        itinerary = deepcopy(self.itinerary_template)

        aircraft = Aircraft("F1", "M1", self.n1, State.stop)
        aircraft.set_location(self.n1)
        self.assertEqual(aircraft.state, State.stop)

        # Stop state
        aircraft.tick()
        self.assertEqual(aircraft.itinerary, None)

        # Moving state
        aircraft.set_itinerary(itinerary)
        self.assertTrue(aircraft.itinerary)
        self.assertEqual(aircraft.state, State.moving)
        self.assertEqual(aircraft.itinerary.current_target, self.n1)

        aircraft.tick()
        self.assertEqual(aircraft.itinerary.current_target, self.n2)

        aircraft.tick()
        self.assertEqual(aircraft.itinerary.current_target, self.n3)

        aircraft.tick()
        self.assertTrue(aircraft.itinerary.is_completed)

    def test_tick_with_delay(self):

        itinerary = deepcopy(self.itinerary_template)

        aircraft = Aircraft("F1", "M1", self.n1, State.stop)
        aircraft.set_location(self.n1)
        self.assertEqual(aircraft.state, State.stop)

        # Stop state
        aircraft.tick()
        self.assertEqual(aircraft.itinerary, None)

        # Moving state
        aircraft.set_itinerary(itinerary)
        self.assertTrue(aircraft.itinerary)
        self.assertEqual(aircraft.state, State.moving)
        self.assertEqual(aircraft.itinerary.current_target, self.n1)

        # targets: n1 - n2 - n3
        aircraft.add_uncertainty_delay()
        # targets: n1 - n1 - n2 - n3

        aircraft.tick()
        # targets: n1 - n2 - n3
        self.assertEqual(aircraft.itinerary.current_target, self.n1)

        aircraft.add_uncertainty_delay()
        # targets: n1 - n1 - n2 - n3
        self.assertEqual(aircraft.itinerary.current_target, self.n1)

        aircraft.tick()
        # targets: n1 - n2 - n3
        self.assertEqual(aircraft.itinerary.current_target, self.n1)

        aircraft.tick()
        # targets: n2 - n3
        self.assertEqual(aircraft.itinerary.current_target, self.n2)
