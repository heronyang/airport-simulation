#!/usr/bin/env python

import datetime
from clock import Clock
from node import Node
from airport import AirportFactory
from aircraft import Aircraft, State
from node import get_middle_node
from config import Config

import sys
import unittest
sys.path.append('..')


class TestAirport(unittest.TestCase):

    n1 = Node("N2", {"lat": 47.822000, "lng": -122.079057})
    n2 = Node("N1", {"lat": 47.722000, "lng": -122.079057})

    n1_260ft = Node("N1_FAR", {"lat": 47.822, "lng": -122.07799})
    n1_240ft = Node("N1_CLOSE", {"lat": 47.82199, "lng": -122.08001})

    class SimulationMock():
        @property
        def now(self):
            return datetime.time(0, 0)

    def test_conflicts_at_node(self):

        simulation = self.SimulationMock()
        airport = AirportFactory.create(simulation, "simple")

        a1 = Aircraft(simulation, "A1", None, self.n1, State.stop)
        a2 = Aircraft(simulation, "A2", None, self.n1, State.stop)

        airport.aircrafts.append(a1)
        airport.aircrafts.append(a2)

        # Get only one conflict
        self.assertEqual(len(airport.conflicts_at_node), 1)

        # Test if the conflict looks like what we expected
        conflict = airport.conflicts_at_node[0]
        self.assertEqual(conflict.location, self.n1)
        self.assertEqual(len(conflict.aircrafts), 2)
        self.assertTrue(a1 in conflict.aircrafts)
        self.assertTrue(a2 in conflict.aircrafts)

        # Add one more aircraft to the same spot
        a3 = Aircraft(simulation, "A3", None, self.n1, State.stop)
        airport.aircrafts.append(a3)

        # Test if the third aircraft shown in conflict correctly
        self.assertEqual(len(airport.conflicts_at_node), 1)
        conflict = airport.conflicts_at_node[0]
        self.assertEqual(conflict.location, self.n1)
        self.assertEqual(len(conflict.aircrafts), 3)
        self.assertTrue(a3 in conflict.aircrafts)

    def test_conflicts(self):

        Config.params["simulation"]["separation"] = 250

        simulation = self.SimulationMock()
        airport = AirportFactory.create(simulation, "simple")

        a1 = Aircraft(simulation, "A1", None, self.n1, State.stop)
        a2 = Aircraft(simulation, "A2", None, self.n1_240ft, State.stop)

        airport.aircrafts.append(a1)
        airport.aircrafts.append(a2)

        # Get only one conflict
        self.assertEqual(len(airport.conflicts), 1)

        # Test if the conflict looks like what we expected
        conflict = airport.conflicts[0]
        self.assertTrue(conflict.location.is_close_to(
            get_middle_node(self.n1, self.n1_240ft)))
        self.assertEqual(len(conflict.aircrafts), 2)
        self.assertTrue(a1 in conflict.aircrafts)
        self.assertTrue(a2 in conflict.aircrafts)

        # Add one far aircraft to the same spot
        a3 = Aircraft(simulation, "A3", None, self.n1_260ft, State.stop)
        airport.aircrafts.append(a3)

        # Test if the third aircraft shown in conflict correctly
        self.assertEqual(len(airport.conflicts), 1)
