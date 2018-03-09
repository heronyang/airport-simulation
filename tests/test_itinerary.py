#!/usr/bin/env python

from copy import deepcopy
from clock import Clock
from datetime import time
from node import Node
from itinerary import Itinerary
from utils import get_seconds_after

import sys
import unittest
sys.path.append('..')


class TestItinerary(unittest.TestCase):

    n1 = Node("N1", {"lat": 47.722000, "lng": -122.079057})
    n2 = Node("N2", {"lat": 47.822000, "lng": -122.079057})
    n3 = Node("N3", {"lat": 47.922000, "lng": -122.079057})

    targets = [
        Itinerary.Target(n1, time(0, 2), time(0, 3)),
        Itinerary.Target(n2, time(0, 5), time(0, 7)),
        Itinerary.Target(n3, time(0, 9), None),
    ]
    itinerary_template = Itinerary(targets)

    def test_init(self):

        # Makes sure the nodes are not too close
        self.assertFalse(self.n1.is_close_to(self.n2))
        self.assertFalse(self.n2.is_close_to(self.n3))

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        clock = Clock()
        self.assertFalse(itinerary.is_completed)
        self.assertEqual(itinerary.next_target.node, self.n1)

    def test_is_completed(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        for i in range(3):
            itinerary.pop_target()

        self.assertTrue(itinerary.is_completed)

    def test_pop_node(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        self.assertEqual(itinerary.pop_target().node, self.n1)
        self.assertEqual(itinerary.pop_target().node, self.n2)
        self.assertEqual(itinerary.pop_target().node, self.n3)
        self.assertRaises(Exception, itinerary.pop_target)

    def test_next_target(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        self.assertEqual(itinerary.next_target.node, self.n1)
        itinerary.pop_target()
        self.assertEqual(itinerary.next_target.node, self.n2)
        itinerary.pop_target()
        self.assertEqual(itinerary.next_target.node, self.n3)
        itinerary.pop_target()

        try:
            itinerary.next_target
            raise Exception("next_target failed to raise exception on error")
        except Exception:
            pass

    def test_add_delay(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        self.assertEqual(itinerary.next_target.node, self.n1)
        itinerary.add_delay(10)
        target = itinerary.pop_target()
        self.assertEqual(target.edt, time(0, 3, 10))

        self.assertEqual(itinerary.next_target.node, self.n2)
        itinerary.add_delay(20)
        target = itinerary.pop_target()
        self.assertEqual(target.edt, time(0, 7, 30))

        self.assertEqual(itinerary.next_target.node, self.n3)
        itinerary.pop_target()

        # If the itinerary is empty, it should not raise error
        itinerary.add_delay(10)
