#!/usr/bin/env python

import datetime
from node import Node
from airport import AirportFactory
from aircraft import Aircraft, State
from config import Config

import sys
import unittest
sys.path.append('..')


class TestAirport(unittest.TestCase):

    Config.params["simulator"]["test_mode"] = True

    n1 = Node("N1", {"lat": 47.822000, "lng": -122.079057})
    n2 = Node("N2", {"lat": 47.822, "lng": -122.07799})
    n3 = Node("N3", {"lat": 47.82199, "lng": -122.08001})

    class SimulationMock():
        @property
        def now(self):
            return datetime.time(0, 0)

    def test_conflicts(self):

        simulation = self.SimulationMock()
        airport = AirportFactory.create(simulation, "simple")

        a1 = Aircraft("A1", None, self.n1, State.stop)
        a2 = Aircraft("A2", None, self.n1, State.stop)
        a3 = Aircraft("A3", None, self.n2, State.stop)

        airport.add_aircraft(a1)
        airport.add_aircraft(a2)
        airport.add_aircraft(a3)

        # Get only one conflict
        self.assertEqual(len(airport.conflicts), 1)

        # Test if the conflict looks like what we expected
        conflict = airport.conflicts[0]
        self.assertTrue(conflict.location == self.n1)
        self.assertEqual(len(conflict.aircrafts), 2)
        self.assertTrue(a1 in conflict.aircrafts)
        self.assertTrue(a2 in conflict.aircrafts)

        # Add one far aircraft to the same spot
        a4 = Aircraft("A4", None, self.n1, State.stop)
        airport.add_aircraft(a4)

        # Test if the third aircraft shown in conflict correctly
        self.assertEqual(len(airport.conflicts), 3)
