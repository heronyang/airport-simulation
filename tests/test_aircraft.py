#!/usr/bin/env python

import sys
import unittest
sys.path.append('..')

from node import Node
from aircraft import Aircraft, State
from itinerary import Itinerary
from clock import Clock
from datetime import time
from copy import deepcopy

class TestAircraft(unittest.TestCase):

    # Overrides the sim_time to 60
    clock = Clock()
    Clock.sim_time = 60

    # Generates a itinerary_template
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

    # [start]----------[n1]----------[n2]---------[n3]
    # 00-------------A01--D02------A03--D04------A05--

    # pilot state / itinerary start_time
    # 00:00: scheduled,     start_time = 00:01 (default start time)
    # 00:01: scheduled,     start_time = 00:02 (n1's departure time)
    # 00:02: moving,        start_time = 00:02
    # 00:03: scheduled,     start_time = 00:04 (n2's departure time)
    # 00:04: moving,        start_time = 00:04

    def test_init(self):

        aircraft = Aircraft("F1", "M1", self.n1)
        aircraft.set_location(self.n1)
        self.assertEqual(aircraft.location, self.n1)

    def test_tick(self):

        itinerary = deepcopy(self.itinerary_template)

        Clock.now = time(0, 0)
        # from IPython.core.debugger import Tracer; Tracer()()

        aircraft = Aircraft("F1", "M1", self.n1)
        aircraft.set_location(self.n1)
        aircraft.set_itinerary(itinerary)
        self.assertEqual(aircraft.pilot.itinerary.start_time, time(0, 1))

        # Moves to time(0, 1)
        self.clock.tick()
        aircraft.pilot.tick(uc = None, flight = None)

        self.assertEqual(Clock.now, time(0, 1))
        self.assertEqual(aircraft.location, self.n1)
        self.assertEqual(aircraft.pilot.state, State.scheduled)
        self.assertEqual(aircraft.pilot.itinerary.start_time, time(0, 2))

        # Moves to time(0, 2)
        self.clock.tick()
        aircraft.pilot.tick(uc = None, flight = None)

        self.assertEqual(Clock.now, time(0, 2))
        self.assertEqual(aircraft.location, self.n1)
        self.assertEqual(aircraft.pilot.state, State.moving)
        self.assertEqual(aircraft.pilot.itinerary.start_time, time(0, 2))

        # Moves to time(0, 3)
        self.clock.tick()
        aircraft.pilot.tick(uc = None, flight = None)

        self.assertEqual(Clock.now, time(0, 3))
        self.assertEqual(aircraft.location, self.n2)    # arrives n2
        self.assertEqual(aircraft.pilot.state, State.scheduled)
        self.assertEqual(aircraft.pilot.itinerary.start_time, time(0, 4))

        # Moves to time(0, 4)
        self.clock.tick()
        aircraft.pilot.tick(uc = None, flight = None)

        self.assertEqual(Clock.now, time(0, 4))
        self.assertEqual(aircraft.location, self.n2)
        self.assertEqual(aircraft.pilot.state, State.moving)
        self.assertEqual(aircraft.pilot.itinerary.start_time, time(0, 4))

        # Moves to time(0, 5)
        self.clock.tick()
        aircraft.pilot.tick(uc = None, flight = None)

        self.assertEqual(Clock.now, time(0, 5))
        self.assertEqual(aircraft.location, self.n3)
        self.assertEqual(aircraft.pilot.state, State.idle)
