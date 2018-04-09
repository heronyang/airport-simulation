#!/usr/bin/env python

from config import Config
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

    Config.params["simulator"]["test_mode"] = True

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
        self.assertEqual(itinerary.current_target, self.n1)

    def test_is_completed(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        for i in range(3):
            itinerary.tick()

        self.assertTrue(itinerary.is_completed)

    def test_tick(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        self.assertEqual(itinerary.current_target, self.n1)
        itinerary.tick()
        self.assertEqual(itinerary.current_target, self.n2)
        itinerary.tick()
        self.assertEqual(itinerary.current_target, self.n3)

    def test_current_target(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        self.assertEqual(itinerary.current_target, self.n1)
        itinerary.tick()
        self.assertEqual(itinerary.current_target, self.n2)
        itinerary.tick()
        self.assertEqual(itinerary.current_target, self.n3)
        itinerary.tick()
        self.assertEqual(itinerary.current_target, None)
        itinerary.tick()
        self.assertEqual(itinerary.current_target, None)

    def test_next_target(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

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
        # [n1] - n2 - n3
        self.assertEqual(itinerary.current_target, self.n1)

        itinerary.add_uncertainty_delay()
        # [n1] - n1 - n2 - n3

        itinerary.tick()
        # n1 - [n1] - n2 - n3
        self.assertEqual(itinerary.current_target, self.n1)

        itinerary.tick()
        # n1 - n1 - [n2] - n3
        self.assertEqual(itinerary.current_target, self.n2)

    def test_reset(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        itinerary.tick()
        itinerary.tick()
        itinerary.tick()
        itinerary.tick()
        itinerary.tick()
        
        itinerary.reset()
        self.assertEqual(itinerary.current_target, self.n1)
        self.assertEqual(itinerary.next_target, self.n2)

    def test_is_delayed(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        # [n1] - n2 - n3
        self.assertFalse(itinerary.is_delayed)
        itinerary.add_uncertainty_delay()
        # [n1] - n1 - n2 - n3
        self.assertTrue(itinerary.is_delayed)

        itinerary.tick()
        self.assertFalse(itinerary.is_delayed)
        itinerary.add_scheduler_delay()
        # n1 - [n1] - n1 - n2 - n3
        self.assertTrue(itinerary.is_delayed)
