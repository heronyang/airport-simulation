#!/usr/bin/env python3

from node import Node
from aircraft import Aircraft, State
from itinerary import Itinerary
from datetime import time
from copy import deepcopy
from clock import Clock
from config import Config

import sys
import unittest
import logging
sys.path.append('..')


class TestAircraft(unittest.TestCase):

    # Generates a itinerary_template
    n1 = Node("N1", {"lat": 47.722000, "lng": -122.079057})
    n2 = Node("N2", {"lat": 47.822000, "lng": -122.079057})
    n3 = Node("N3", {"lat": 47.922000, "lng": -122.079057})

    m1 = Node("M1", {"lat": 47.772000, "lng": -122.079057})
    m2 = Node("M2", {"lat": 47.872000, "lng": -122.079057})

    m = Node("M", {"lat": 47.755333, "lng": -122.079057})

    targets = [
        Itinerary.Target(n1, time(0, 2), time(0, 3)),
        Itinerary.Target(n2, time(0, 5), time(0, 7)),
        Itinerary.Target(n3, time(0, 9), None),
    ]
    itinerary_template = Itinerary(targets)

    # -----[start]-------[n1]------------[n2]---------[n3]----
    # -----[start]---------------[m1]------------[m2]---------
    # 00------01------A02----D03------A05----D07------A09-----
    # -------stop------|-hold-|-moving-|-hold-|-moving-|-stop-


    class SimulationMock():

        class AirportMock():

            def update_aircraft_location(a, b, c, d):
                pass

        def __init__(self, clock):
            self.clock = clock
            self.airport = self.AirportMock()

        def tick(self):
            self.clock.tick()

        @property
        def now(self):
            return self.clock.now

    def test_init(self):

        simulation = self.SimulationMock(Clock())
        aircraft = Aircraft(simulation, "F1", "M1", self.n1, State.unknown)
        aircraft.set_location(self.n1)
        self.assertEqual(aircraft.location, self.n1)

    def test_tick(self):

        # Overrides the time unit to 60 seconds
        Config.params["simulation"]["time_unit"] = 60
        itinerary = deepcopy(self.itinerary_template)
        itinerary.set_quiet(logging.getLogger("QUIET_MODE"))
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
        self.assertEqual(len(aircraft.pilot.itinerary.targets), 3)

        # [00:03] Finishes n1
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 3))

        self.assertEqual(aircraft.location, self.n2)
        self.assertTrue(aircraft.true_location.is_close_to(self.n1))
        self.assertEqual(aircraft.state, State.moving)
        self.assertEqual(len(aircraft.pilot.itinerary.targets), 2)

        # [00:04] Moving toward n2
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 4))

        self.assertEqual(aircraft.location, self.n2)
        self.assertTrue(aircraft.true_location.is_close_to(self.m1))
        self.assertEqual(aircraft.state, State.moving)
        self.assertEqual(len(aircraft.pilot.itinerary.targets), 2)

        # [00:05] Arrived n2
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 5))

        self.assertEqual(aircraft.location, self.n2)
        self.assertEqual(aircraft.state, State.hold)
        self.assertEqual(len(aircraft.pilot.itinerary.targets), 2)

        # [00:06] Arrived n2
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 6))

        self.assertEqual(aircraft.location, self.n2)
        self.assertEqual(aircraft.state, State.hold)
        self.assertEqual(len(aircraft.pilot.itinerary.targets), 2)

        # [00:07] Leaving n2
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 7))

        self.assertEqual(aircraft.location, self.n3)
        self.assertTrue(aircraft.true_location.is_close_to(self.n2))
        self.assertEqual(aircraft.state, State.moving)
        self.assertEqual(len(aircraft.pilot.itinerary.targets), 1)

        # [00:08] Moving toward n3
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 8))

        self.assertEqual(aircraft.location, self.n3)
        self.assertTrue(aircraft.true_location.is_close_to(self.m2))
        self.assertEqual(aircraft.state, State.moving)
        self.assertEqual(len(aircraft.pilot.itinerary.targets), 1)

        # [00:09] Arrived n3
        self.assertFalse(aircraft.pilot.itinerary.is_completed)
        simulation.tick()
        aircraft.pilot.tick()
        self.assertEqual(simulation.clock.now, time(0, 9))

        self.assertEqual(aircraft.location, self.n3)
        self.assertEqual(aircraft.state, State.stop)
        self.assertEqual(aircraft.pilot.itinerary, None)

    def test_tick_with_delay(self):

        # -----[start]-------[n1]------------[n2]-
        # 00------01------A02----D03------A05-----
        # -------stop------|-hold-|-moving-|-hold-

        # Adds delay 30s
        # -----[start]-------[n1]---[m]------[n2]-
        # 00------01------A02----D0330------A05---
        # -------stop------|-hold-|-moving-|-hold-


        # Overrides the time unit to 60 seconds
        Config.params["simulation"]["time_unit"] = 60
        itinerary = deepcopy(self.itinerary_template)
        itinerary.set_quiet(logging.getLogger("QUIET_MODE"))
        simulation = self.SimulationMock(Clock())

        # [00:00] Setups the aircraft in init state
        self.assertEqual(simulation.clock.now, time(0, 0))
        aircraft = Aircraft(simulation, "F1", "M1", self.n1, State.stop)
        aircraft.set_location(self.n1)

        # [00:01] Assigns an itinerary for this aircraft
        simulation.tick()
        aircraft.pilot.tick()
        aircraft.set_itinerary(itinerary)

        # [00:02] Itinerary starts and state changed to hold
        simulation.tick()
        aircraft.pilot.tick()

        # Adds delay
        aircraft.pilot.itinerary.add_delay(30)

        # [00:03] Still hold at n1
        simulation.tick()
        aircraft.pilot.tick()

        self.assertEqual(aircraft.location, self.n1)
        self.assertTrue(aircraft.true_location.is_close_to(self.n1))
        self.assertEqual(aircraft.state, State.hold)
        self.assertEqual(len(aircraft.pilot.itinerary.targets), 3)

        # [00:04] Leave n1
        simulation.tick()
        aircraft.pilot.tick()

        self.assertEqual(aircraft.location, self.n2)
        self.assertTrue(aircraft.true_location.is_close_to(self.m))
        self.assertEqual(aircraft.state, State.moving)
        self.assertEqual(len(aircraft.pilot.itinerary.targets), 2)
