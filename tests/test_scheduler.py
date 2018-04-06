#!/usr/bin/env python3
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

    a1 = Aircraft(None, "A1", None, g1, State.stop)
    a2 = Aircraft(None, "A2", None, g2, State.stop)
    a3 = Aircraft(None, "A3", None, g2, State.stop)

    conflicts_is_called = True

    class AirportMock():

        def __init__(self, simulation, aircraft1, aircraft2):
            aircraft1.simulation = simulation
            aircraft2.simulation = simulation
            self.aircrafts = [aircraft1, aircraft2]

            self.aircraft1 = aircraft1
            self.aircraft2 = aircraft2

        def apply_schedule(self, schedule):
            return Schedule({}, 0)

        @property
        def conflicts(self):
            if TestScheduler.conflicts_is_called:
                return []
            TestScheduler.conflicts_is_called = True
            return [Conflict(None, [self.aircraft1, self.aircraft2], None)]

    class RunwayMock():

        def __init__(self, runway_start):
            self.runway_start = runway_start

        @property
        def start(self):
            return self.runway_start

    class ClockMock():

        def tick(self):
            pass

    class ScenarioMock():

        def __init__(self, g1, g2, s1, runway_start):
            self.runway = TestScheduler.RunwayMock(runway_start)
            self.g1, self.g2, self.s1 = g1, g2, s1

        def get_flight(self, aircraft):
            if aircraft.callsign == "A1":
                return DepartureFlight(
                    None, "A1", None, None, self.g1, self.s1,
                    self.runway, time(2, 37), time(2, 37)
                )
            elif aircraft.callsign == "A2":
                return DepartureFlight(
                    None, "A2", None, None, self.g2, self.s1,
                    self.runway, time(2, 36), time(2, 36)
                )
            elif aircraft.callsign == "A3":
                return DepartureFlight(
                    None, "A3", None, None, self.g2, self.s1,
                    self.runway, time(2, 37, 1), time(2, 37, 1)
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

            else:
                raise Exception("Unsupported routing query")

    class SimulationMock():

        def __init__(self, a1, a2, g1, g2, s1, runway_start):
            self.airport = TestScheduler.AirportMock(self, a1, a2)
            self.scenario = TestScheduler.ScenarioMock(
                g1, g2, s1, runway_start)
            self.routing_expert = TestScheduler.RoutingExpertMock(
                g1, g2, s1, runway_start)
            self.clock = TestScheduler.ClockMock()

        def remove_aircrafts(self):
            pass

        def quiet_tick(self):
            pass

        @property
        def now(self):
            return time(2, 30)

        @property
        def copy(self):
            return deepcopy(self)

    def test_deterministic_scheduler(self):

        Config.params["scheduler"]["name"] = "deterministic_scheduler"

        # Overrides the tightness and velocity
        tightness = 120
        velocity = 5
        Config.params["scheduler"]["tightness"] = tightness
        Config.params["scheduler"]["velocity"] = velocity

        # Create mock objects, then schedule it
        simulation = self.SimulationMock(self.a1, self.a2, self.g1, self.g2,
                                         self.s1, self.runway_start)
        scheduler = get_scheduler()
        schedule = scheduler.schedule(simulation)

        self.assertEqual(len(schedule.itineraries), 2)

        # a2 has an early departure time, so it goes first
        self.assertTrue(self.a2 in schedule.itineraries)
        self.assertTrue(self.a1 in schedule.itineraries)

        # Gets itineraries
        iti1 = schedule.itineraries[self.a1]
        iti2 = schedule.itineraries[self.a2]

        self.assertEqual(iti2.targets[0].eat, time(2, 36, 0))
        self.assertEqual(iti2.targets[0].edt, time(2, 36, 0))
        self.assertEqual(iti2.targets[1].eat, time(2, 48, 10))
        self.assertEqual(iti2.targets[1].edt, time(2, 48, 10))
        self.assertEqual(iti2.targets[2].eat, time(2, 56, 22))
        self.assertEqual(iti2.targets[2].edt, time(2, 56, 22))

        self.assertEqual(iti1.targets[0].eat, time(2, 37, 0))
        self.assertEqual(iti1.targets[0].edt, time(2, 37, 0))
        self.assertEqual(
            iti1.targets[1].eat,
            get_seconds_after(iti2.targets[1].eat, tightness)
        )
        self.assertEqual(
            iti1.targets[1].edt,
            get_seconds_after(iti2.targets[1].edt, tightness)
        )
        self.assertEqual(
            iti1.targets[2].eat,
            get_seconds_after(iti2.targets[2].eat, tightness)
        )
        self.assertEqual(
            iti1.targets[2].edt,
            get_seconds_after(iti2.targets[2].edt, tightness)
        )

    def test_deterministic_continuous_scheduler_no_conflict(self):

        Config.params["scheduler"]["name"] = \
                "deterministic_continuous_scheduler"

        velocity = 5
        Config.params["scheduler"]["velocity"] = velocity
        Config.params["scheduler"]["delay_time"] = 10

        # Create mock objects, then schedule it
        simulation = self.SimulationMock(
            self.a1, self.a2, self.g1, self.g2, self.s1, self.runway_start)
        scheduler = get_scheduler()
        schedule = scheduler.schedule(simulation)

        self.assertEqual(len(schedule.itineraries), 2)

        # a2 has an early departure time, so it goes first
        self.assertTrue(self.a2 in schedule.itineraries)
        self.assertTrue(self.a1 in schedule.itineraries)

        # Gets itineraries
        iti1 = schedule.itineraries[self.a1]
        iti2 = schedule.itineraries[self.a2]

        self.assertEqual(iti2.targets[0].eat, time(2, 36, 0))
        self.assertEqual(iti2.targets[0].edt, time(2, 36, 0))
        self.assertEqual(iti2.targets[1].eat, time(2, 48, 10))
        self.assertEqual(iti2.targets[1].edt, time(2, 48, 10))
        self.assertEqual(iti2.targets[2].eat, time(2, 56, 22))
        self.assertEqual(iti2.targets[2].edt, time(2, 56, 22))

        self.assertEqual(iti1.targets[0].eat, time(2, 37, 0))
        self.assertEqual(iti1.targets[0].edt, time(2, 37, 0))
        self.assertEqual(iti1.targets[1].eat, time(2, 49, 10))
        self.assertEqual(iti1.targets[1].edt, time(2, 49, 10))
        self.assertEqual(iti1.targets[2].eat, time(2, 57, 22))
        self.assertEqual(iti1.targets[2].edt, time(2, 57, 22))

    def test_deterministic_continuous_scheduler_one_conflict(self):

        Config.params["scheduler"]["name"] = \
                "deterministic_continuous_scheduler"

        TestScheduler.conflicts_is_called = False
        velocity = 5
        Config.params["scheduler"]["velocity"] = velocity
        Config.params["scheduler"]["delay_time"] = 10

        # Create mock objects, then schedule it
        simulation = self.SimulationMock(
            self.a1, self.a3, self.g1, self.g2, self.s1, self.runway_start)
        scheduler = get_scheduler()
        schedule = scheduler.schedule(simulation)

        self.assertEqual(len(schedule.itineraries), 2)

        self.assertTrue(self.a3 in schedule.itineraries)
        self.assertTrue(self.a1 in schedule.itineraries)

        # Gets itineraries
        iti1 = schedule.itineraries[self.a1]
        iti3 = schedule.itineraries[self.a3]

        self.assertEqual(iti1.targets[0].eat, time(2, 37, 0))
        self.assertEqual(iti1.targets[0].edt, time(2, 37, 0))
        self.assertEqual(iti1.targets[1].eat, time(2, 49, 10))
        self.assertEqual(iti1.targets[1].edt, time(2, 49, 10))
        self.assertEqual(iti1.targets[2].eat, time(2, 57, 22))
        self.assertEqual(iti1.targets[2].edt, time(2, 57, 22))

        self.assertEqual(iti3.targets[0].eat, time(2, 37, 1))
        self.assertEqual(iti3.targets[0].edt, time(2, 37, 11))
        self.assertEqual(iti3.targets[1].eat, time(2, 49, 11))
        self.assertEqual(iti3.targets[1].edt, time(2, 49, 21))
        self.assertEqual(iti3.targets[2].eat, time(2, 57, 23))
        self.assertEqual(iti3.targets[2].edt, time(2, 57, 33))

