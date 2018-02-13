#!/usr/bin/env python

import sys
import unittest
sys.path.append('..')

from node import Node
from aircraft import Aircraft, State
from itinerary import Itinerary
from datetime import time
from copy import deepcopy
from clock import Clock
from config import Config

class TestAircraft(unittest.TestCase):

    # Generates a itinerary_template
    n1 = Node(0, "N1", {"lat": 47.722000, "lng": -122.079057})
    n2 = Node(0, "N2", {"lat": 47.822000, "lng": -122.079057})
    n3 = Node(0, "N3", {"lat": 47.922000, "lng": -122.079057})

    target_nodes = [
        Itinerary.TargetNode(n1, time(0, 2), time(0, 3)),
        Itinerary.TargetNode(n2, time(0, 5), time(0, 7)),
        Itinerary.TargetNode(n3, time(0, 9), None),
    ]
    itinerary_template = Itinerary(target_nodes)

    # -----[start]-------[n1]------------[n2]---------[n3]----
    # 00------01------A02----D03------A05----D07------A09-----
    # -------stop------|-hold-|-moving-|-hold-|-moving-|-stop-

    class SimulationMock():
        def __init__(self, clock):
            self.clock = clock

        def tick(self):
            self.clock.tick()

    def test_init(self):

        aircraft = Aircraft(None, "F1", "M1", self.n1, State.unknown)
        aircraft.set_location(self.n1)
        self.assertEqual(aircraft.location, self.n1)

    def test_tick(self):

        # Overrides the time unit to 60 seconds
        Config.params["simulation"]["time_unit"] = 60
        itinerary = deepcopy(self.itinerary_template)
        simulation = self.SimulationMock(Clock())

        # [00:00] Setups the aircraft in init state
        self.assertEqual(simulation.clock.now, time(0, 0))
        aircraft = Aircraft(simulation, "F1", "M1", self.n1, State.stop)
        aircraft.set_location(self.n1)
        self.assertEqual(aircraft.state, State.stop)

        # [00:01] Assigns an itinerary for this aircraft
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 1))
        self.assertEqual(aircraft.pilot.itinerary, None)
        aircraft.set_itinerary(itinerary)
        self.assertTrue(aircraft.pilot.itinerary)
        self.assertEqual(aircraft.state, State.stop)

        # [00:02] Itinerary starts and state changed to hold
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 2))

        self.assertEqual(aircraft.location, self.n1)
        self.assertEqual(aircraft.state, State.hold)
        self.assertEqual(len(aircraft.pilot.itinerary.target_nodes), 3)

        # [00:03] Finishes n1
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 3))

        self.assertEqual(aircraft.location, self.n2)
        self.assertEqual(aircraft.state, State.moving)
        self.assertEqual(len(aircraft.pilot.itinerary.target_nodes), 2)

        # [00:04] Moving toward n2
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 4))

        self.assertEqual(aircraft.location, self.n2)
        self.assertEqual(aircraft.state, State.moving)
        self.assertEqual(len(aircraft.pilot.itinerary.target_nodes), 2)

        # [00:05] Arrived n2
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 5))

        self.assertEqual(aircraft.location, self.n2)
        self.assertEqual(aircraft.state, State.hold)
        self.assertEqual(len(aircraft.pilot.itinerary.target_nodes), 2)

        # [00:06] Arrived n2
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 6))

        self.assertEqual(aircraft.location, self.n2)
        self.assertEqual(aircraft.state, State.hold)
        self.assertEqual(len(aircraft.pilot.itinerary.target_nodes), 2)

        # [00:07] Leaving n2
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 7))

        self.assertEqual(aircraft.location, self.n3)
        self.assertEqual(aircraft.state, State.moving)
        self.assertEqual(len(aircraft.pilot.itinerary.target_nodes), 1)

        # [00:08] Moving toward n3
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 8))

        self.assertEqual(aircraft.location, self.n3)
        self.assertEqual(aircraft.state, State.moving)
        self.assertEqual(len(aircraft.pilot.itinerary.target_nodes), 1)

        # [00:09] Arrived n3
        self.assertFalse(aircraft.pilot.itinerary.is_completed)
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 9))

        self.assertEqual(aircraft.location, self.n3)
        self.assertEqual(aircraft.state, State.stop)
        self.assertEqual(aircraft.pilot.itinerary, None)
