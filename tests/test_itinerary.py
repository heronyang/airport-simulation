#!/usr/bin/env python

from copy import deepcopy
from clock import Clock
from datetime import time
from node import Node
from itinerary import Itinerary

import sys
import unittest
import logging
sys.path.append('..')


class TestItinerary(unittest.TestCase):

    n1 = Node("N1", {"lat": 47.722000, "lng": -122.079057})
    n2 = Node("N2", {"lat": 47.822000, "lng": -122.079057})
    n3 = Node("N3", {"lat": 47.922000, "lng": -122.079057})

    itinerary_template = Itinerary(targets=[n1, n2, n3])

    def test_init(self):

        # Makes sure the nodes are not too close
        self.assertFalse(self.n1.is_close_to(self.n2))
        self.assertFalse(self.n2.is_close_to(self.n3))

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        clock = Clock()
        self.assertFalse(itinerary.is_completed)
        self.assertEqual(itinerary.next_target, self.n1)

    def test_is_completed(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        for i in range(3):
            itinerary.tick()

        self.assertTrue(itinerary.is_completed)

    def test_tick(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        self.assertEqual(itinerary.next_target, self.n1)
        itinerary.tick()
        self.assertEqual(itinerary.next_target, self.n2)
        itinerary.tick()
        self.assertEqual(itinerary.next_target, self.n3)

    def test_next_target(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        self.assertEqual(itinerary.next_target, self.n1)
        itinerary.tick()
        self.assertEqual(itinerary.next_target, self.n2)
        itinerary.tick()
        self.assertEqual(itinerary.next_target, self.n3)
        itinerary.tick()
        self.assertEqual(itinerary.next_target, None)
        itinerary.tick()
        self.assertEqual(itinerary.next_target, None)

    def test_add_delay(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        self.assertEqual(itinerary.next_target, self.n1)
        itinerary.add_delay()
        target = itinerary.tick()
        self.assertEqual(itinerary.next_target, self.n1)

        target = itinerary.tick()
        self.assertEqual(itinerary.next_target, self.n2)
