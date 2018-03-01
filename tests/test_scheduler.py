#!/usr/bin/env python3
from datetime import time
from aircraft import Aircraft, State
from flight import DepartureFlight
from scheduler import Scheduler
from node import Node
from surface import RunwayNode, Spot
from config import Config
from utils import get_seconds_after

import sys
import unittest
sys.path.append('..')


class TestScheduler(unittest.TestCase):

    #     (G1)
    #      |
    #      | <3647.9 ft, 12.2 mins>
    #      |
    #     (S1)-----<4913.3 ft, 16.4 mins>-----(RANWAY.start)
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

    class AirportMock():

        def __init__(self, simulation, a1, a2):
            a1.simulation = simulation
            a2.simulation = simulation
            self.aircrafts = [a1, a2]

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
                    None, "A1", None, None, self.g1, self.s1,
                    self.runway, time(2, 37), time(2, 30)
                )
            elif aircraft.callsign == "A2":
                return DepartureFlight(
                    None, "A2", None, None, self.g2, self.s1,
                    self.runway, time(2, 36), time(2, 30)
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
            self.scenario = TestScheduler.ScenarioMock(g1, g2, s1,
                                                       runway_start)
            self.routing_expert = TestScheduler.RoutingExpertMock(g1, g2, s1,
                                                                  runway_start)

        @property
        def now(self):
            return time(2, 30)

    def test_basic(self):

        # Overrides the tightness and velocity
        tightness = 120
        velocity = 5
        Config.params["scheduler"]["tightness"] = tightness
        Config.params["scheduler"]["velocity"] = velocity

        # Create mock objects, then schedule it
        simulation = self.SimulationMock(self.a1, self.a2, self.g1, self.g2,
                                         self.s1, self.runway_start)
        scheduler = Scheduler()
        schedule = scheduler.schedule(simulation)

        self.assertEqual(len(schedule.requests), 2)

        # a2 has an early departure time, so it goes first
        self.assertEqual(schedule.requests[0].aircraft, self.a2)
        self.assertEqual(schedule.requests[1].aircraft, self.a1)

        # Gets itineraries
        iti1 = schedule.requests[1].itinerary.target_nodes
        iti2 = schedule.requests[0].itinerary.target_nodes

        self.assertEqual(iti2[0].eat, time(2, 30, 0))
        self.assertEqual(iti2[0].edt, time(2, 30, 0))
        self.assertEqual(iti2[1].eat, time(2, 42, 10))
        self.assertEqual(iti2[1].edt, time(2, 42, 10))
        self.assertEqual(iti2[2].eat, time(2, 50, 22))
        self.assertEqual(iti2[2].edt, time(2, 50, 22))

        self.assertEqual(iti1[0].eat, time(2, 30, 0))
        self.assertEqual(iti1[0].edt, time(2, 30, 0))
        self.assertEqual(iti1[1].eat,
                         get_seconds_after(iti2[1].eat, tightness))
        self.assertEqual(iti1[1].edt,
                         get_seconds_after(iti2[1].edt, tightness))
        self.assertEqual(iti1[2].eat,
                         get_seconds_after(iti2[2].eat, tightness))
        self.assertEqual(iti1[2].edt,
                         get_seconds_after(iti2[2].edt, tightness))
