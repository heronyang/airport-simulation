#!/usr/bin/env python

import sys
import unittest
sys.path.append('..')

from copy import deepcopy
from clock import Clock
from datetime import time
from node import Node
from itinerary import Itinerary
from utils import get_seconds_after

class TestItinerary(unittest.TestCase):

    n1 = Node(0, "N1", {"lat": 47.722000, "lng": -122.079057})
    n2 = Node(0, "N2", {"lat": 47.822000, "lng": -122.079057})
    n3 = Node(0, "N3", {"lat": 47.922000, "lng": -122.079057})

    start_time = time(0, 1)
    target_nodes = [
        Itinerary.TargetNode(n1, start_time, time(0, 2)),
        Itinerary.TargetNode(n2, time(0, 3), time(0, 4)),
        Itinerary.TargetNode(n3, time(0, 5), time(0, 6)),
    ]
    itinerary_template = Itinerary(target_nodes, start_time)

    def test_init(self):

        # Makes sure the nodes are not too close
        self.assertFalse(self.n1.is_close_to(self.n2))
        self.assertFalse(self.n2.is_close_to(self.n3))

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        Clock.now = time(0, 0)
        self.assertFalse(itinerary.is_started)
        self.assertFalse(itinerary.is_completed)
        self.assertEqual(itinerary.peek_target_node().node, self.n1)
        
    def test_is_start(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        Clock.now = time(0, 1)
        self.assertTrue(itinerary.is_started)

    def test_is_completed(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        for i in range(3):
            itinerary.pop_target_node()

        self.assertTrue(itinerary.is_completed)

    def test_pop_target_node(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        self.assertEqual(itinerary.pop_target_node().node, self.n1)
        self.assertEqual(itinerary.pop_target_node().node, self.n2)
        self.assertEqual(itinerary.pop_target_node().node, self.n3)
        self.assertRaises(Exception, itinerary.pop_target_node)

    def test_peek_target_node(self):

        # Gets a copy of the itinerary
        itinerary = deepcopy(self.itinerary_template)

        self.assertEqual(itinerary.peek_target_node().node, self.n1)
        for i in range(3):
            itinerary.pop_target_node()
        self.assertRaises(Exception, itinerary.peek_target_node)
