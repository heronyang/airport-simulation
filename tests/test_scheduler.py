#!/usr/bin/env python3
import logging
from clock import Clock
from copy import deepcopy
from datetime import time
from aircraft import Aircraft, State
from flight import DepartureFlight
from scheduler.deterministic_scheduler import Scheduler
from node import Node
from surface import RunwayNode, Spot
from config import Config
from utils import get_seconds_after
from simulation import get_scheduler
from schedule import Schedule
from conflict import Conflict

import sys
import unittest
sys.path.append('..')


class TestScheduler(unittest.TestCase):

    Config.params["simulator"]["test_mode"] = True
    Config.params["simulation"]["time_unit"] = 30

    #     (G1)
    #      |
    #      | <3647.9 ft, 12.2 mins>
    #      |
    #     (S1)-----<2456.7 ft, 8:11 mins>-----(RANWAY.start)
    #      |
    #      | <3647.9 ft, 12.2 mins>
    #      |
    #     (G2)

    g1 = Node("G1", {"lat": 47.812000, "lng": -122.079057})
    g2 = Node("G2", {"lat": 47.832000, "lng": -122.079057})
    s1 = Spot("S1", {"lat": 47.822000, "lng": -122.079057})
    runway_start = RunwayNode({"lat": 47.822000, "lng": -122.069057})

    a1 = Aircraft("A1", None, g1, State.stop)
    a2 = Aircraft("A2", None, g2, State.stop)
    a3 = Aircraft("A3", None, g2, State.stop)

    a4 = Aircraft("A4", None, s1, State.stop)
    a5 = Aircraft("A5", None, s1, State.stop)

    class AirportMock():

        def __init__(self, simulation, aircraft1, aircraft2):
            self.aircrafts = [aircraft1, aircraft2]
            self.aircraft1 = aircraft1
            self.aircraft2 = aircraft2

        def apply_schedule(self, schedule):
            for aircraft, itinerary in schedule.itineraries.items():
                if aircraft == self.aircraft1:
                    self.aircraft1.set_itinerary(itinerary)
                else:
                    self.aircraft2.set_itinerary(itinerary)

        def set_quiet(self, logger):
            self.aircraft1.logger = logger
            self.aircraft2.logger = logger

        def quiet_tick(self):
            self.aircraft1.tick()
            self.aircraft2.tick()

        @property
        def conflicts(self):
            if self.aircraft1.location == self.aircraft2.location:
                return [Conflict(None, [self.aircraft1, self.aircraft2], None)]
            return []

        @property
        def next_conflicts(self):
            if self.aircraft1.itinerary is None or\
               self.aircraft2.itinerary is None:
                return []
            if self.aircraft1.itinerary.next_target is None or\
               self.aircraft2.itinerary.next_target is None:
                return []
            if self.aircraft1.itinerary.next_target == \
               self.aircraft2.itinerary.next_target:
                return [Conflict(None, [self.aircraft1, self.aircraft2], None)]
            return []

    class RunwayMock():

        def __init__(self, runway_start):
            self.runway_start = runway_start

        @property
        def start(self):
            return self.runway_start

    class ScenarioMock():

        def __init__(self, g1, g2, s1, runway_start):
            self.runway = TestScheduler.RunwayMock(runway_start)
            self.g1, self.g2, self.s1 = g1, g2, s1

        def get_flight(self, aircraft):
            if aircraft.callsign == "A1":
                return DepartureFlight(
                    "A1", None, None, self.g1, self.s1, self.runway,
                    time(2, 36), time(2, 36)
                )
            elif aircraft.callsign == "A2":
                return DepartureFlight(
                    "A2", None, None, self.g2, self.s1, self.runway,
                    time(2, 36, 30), time(2, 36, 30)
                )
            elif aircraft.callsign == "A3":
                return DepartureFlight(
                    "A3", None, None, self.g2, self.s1, self.runway,
                    time(2, 36, 1), time(2, 36, 1)
                )
            elif aircraft.callsign == "A4":
                return DepartureFlight(
                    "A4", None, None, self.g2, self.s1, self.runway,
                    time(2, 36, 1), time(2, 36, 1)
                )
            elif aircraft.callsign == "A5":
                return DepartureFlight(
                    "A5", None, None, self.g2, self.s1, self.runway,
                    time(2, 36, 2), time(2, 36, 2)
                )

    class RouteMock():

        def __init__(self, nodes):
            self.nodes = nodes

    class RoutingExpertMock():

        def __init__(self, g1, g2, s1, runway_start):
            self.g1, self.g2, self.s1 = g1, g2, s1
            self.runway_start = runway_start

        def get_shortest_route(self, src, dst):

            if src == self.g1 and dst == self.runway_start:
                return TestScheduler.RouteMock([self.g1, self.s1,
                                                self.runway_start])

            if src == self.g2 and dst == self.runway_start:
                return TestScheduler.RouteMock([self.g2, self.s1,
                                                self.runway_start])

            if src == self.s1 and dst == self.runway_start:
                return TestScheduler.RouteMock([self.s1, self.runway_start])

            else:
                raise Exception("Unsupported routing query")

    class SimulationMock():

        def __init__(self, a1, a2, g1, g2, s1, runway_start):
            self.airport = TestScheduler.AirportMock(self, a1, a2)
            self.scenario = TestScheduler.ScenarioMock(
                g1, g2, s1, runway_start)
            self.routing_expert = TestScheduler.RoutingExpertMock(
                g1, g2, s1, runway_start)
            self.clock = Clock()
            self.clock.now = time(2, 30)

        def set_quiet(self, logger):
            self.airport.set_quiet(logger)

        def remove_aircrafts(self):
            pass

        def quiet_tick(self):
            self.clock.tick()
            self.airport.quiet_tick()

        @property
        def now(self):
            return self.clock.now

        @property
        def copy(self):
            s = deepcopy(self)
            s.set_quiet(logging.getLogger("QUIET_MODE"))
            return s

    def test_deterministic_scheduler_with_one_conflict(self):

        Config.params["scheduler"]["name"] = "deterministic_scheduler"

        # Create mock objects, then schedule it
        simulation = self.SimulationMock(
            self.a1, self.a3, self.g1, self.g2, self.s1, self.runway_start)
        scheduler = get_scheduler()
        schedule = scheduler.schedule(simulation)

        self.assertEqual(len(schedule.itineraries), 2)

        # a3 has an early departure time, so it goes first
        self.assertTrue(self.a1 in schedule.itineraries)
        self.assertTrue(self.a3 in schedule.itineraries)

        # Gets itineraries
        iti1 = schedule.itineraries[self.a1]
        iti2 = schedule.itineraries[self.a3]

        self.assertEqual(iti1.targets[0], self.g1)
        self.assertEqual(iti1.targets[1], self.s1)
        self.assertEqual(iti1.targets[2], self.runway_start)

        self.assertEqual(iti2.targets[0], self.g2)
        self.assertEqual(iti2.targets[1], self.g2)
        self.assertEqual(iti2.targets[2], self.s1)
        self.assertEqual(iti2.targets[3], self.runway_start)

    def test_deterministic_scheduler_with_one_unsolvable_conflict(self):

        # Sets two aircraft standing at the same node
        self.a4.location = self.s1
        self.a5.location = self.s1

        # Create mock objects, then schedule it
        simulation = self.SimulationMock(
            self.a4, self.a5, self.g1, self.g2, self.s1, self.runway_start)
        scheduler = get_scheduler()
        schedule = scheduler.schedule(simulation)

        self.assertEqual(len(schedule.itineraries), 2)

        # a3 has an early departure time, so it goes first
        self.assertTrue(self.a4 in schedule.itineraries)
        self.assertTrue(self.a5 in schedule.itineraries)

        # Gets itineraries
        iti1 = schedule.itineraries[self.a4]
        iti2 = schedule.itineraries[self.a5]

        self.assertEqual(schedule.n_unsolvable_conflicts, 0)

        self.assertEqual(iti1.targets[0], self.s1)
        self.assertEqual(iti1.targets[1], self.runway_start)

        self.assertEqual(iti2.targets[0], self.s1)
        self.assertEqual(iti2.targets[1], self.s1)
        self.assertEqual(iti2.targets[2], self.runway_start)
