#!/usr/bin/env python

from datetime import time
from config import Config
from simulation import Simulation
from clock import ClockException
from heapdict import heapdict
from schedule import Schedule

import sys
import unittest
sys.path.append('..')


class TestSimulation(unittest.TestCase):

    Config.params["airport"] = "simple"
    Config.params["uncertainty"]["enabled"] = False
    Config.params["simulator"]["test_mode"] = True

    class SchedulerMock():

        def schedule(self, _):
            return Schedule({}, 0)

    def test_init(self):

        simulation = Simulation()

        self.assertEqual(len(simulation.airport.aircrafts), 0)
        self.assertEqual(simulation.now, time(0, 0))

    def test_add_aircrafts(self):

        simulation = Simulation()
        simulation.scheduler = self.SchedulerMock()

        # TODO: Arrivals haven't be considered

        # Finds the first n flights
        n = 3
        departures = simulation.scenario.departures
        if departures is None or len(departures) < n:
            # At least n flight should be contained in the scenario
            raise Exception("Invalid scenario is used")

        h = heapdict()
        for departure in departures:
            h[departure] = departure.appear_time

        for i in range(n):

            # Gets the next flight
            next_flight, _ = h.popitem()

            # Tick til the time the flight appears
            while simulation.now <= next_flight.appear_time:
                simulation.tick()

            # Test if the flight appeared correctly
            self.assertTrue(next_flight.aircraft in
                            simulation.airport.aircrafts)
            self.assertTrue(next_flight.aircraft.location ==
                            next_flight.from_gate)

    def test_add_aircrafts_all(self):

        simulation = Simulation()
        simulation.scheduler = self.SchedulerMock()

        # TODO: Currently we assume that all aircrafts will be added even the
        # gate is occupied
        # TODO: Arrivals haven't be considered
        while True:
            try:
                simulation.tick()
            except ClockException:
                break

        n_aircrafts_in_queue = 0
        for gate, queue in simulation.airport.gate_queue.items():
            n_aircrafts_in_queue += len(queue)
        self.assertEqual(
            len(simulation.scenario.departures),
            len(simulation.airport.aircrafts) + n_aircrafts_in_queue
        )

    def test_remove_aircrafts(self):

        simulation = Simulation()
        simulation.scheduler = self.SchedulerMock()

        departures = simulation.scenario.departures
        if departures is None or len(departures) < 1:
            # At least n flight should be contained in the scenario
            raise Exception("Invalid scenario is used")

        h = heapdict()
        for departure in departures:
            h[departure] = departure.appear_time

        next_flight, _ = h.popitem()

        # Tick til the time the flight appears
        while simulation.now <= next_flight.appear_time:
            simulation.tick()

        n_flight = len(simulation.airport.aircrafts)

        next_flight.aircraft.set_location(next_flight.runway.start)
        simulation.remove_aircrafts()
        self.assertEqual(len(simulation.airport.aircrafts), n_flight - 1)

    def test_gate_queue(self):

        simulation = Simulation()
        simulation.scheduler = self.SchedulerMock()

        departures = simulation.scenario.departures
        if departures is None or len(departures) < 1:
            # At least n flight should be contained in the scenario
            raise Exception("Invalid scenario is used")

        h = heapdict()
        for departure in departures:
            h[departure] = departure.departure_time

        # Gets the first two flights
        f1, _ = h.popitem()
        f2, _ = h.popitem()

        f1.from_gate = f2.from_gate

        # Tick til the time the first flight appears
        while simulation.now <= f1.appear_time:
            simulation.tick()

        self.assertEqual(len(simulation.airport.aircrafts), 1)

        # Tick til the time the second flight appears
        while simulation.now <= f2.appear_time:
            simulation.tick()

        # f1 should be in the airport, f2 is in the gate queue
        self.assertEqual(len(simulation.airport.aircrafts), 1)
        self.assertEqual(len(simulation.airport.gate_queue[f1.from_gate]), 1)
        self.assertTrue(f2.aircraft in 
                        simulation.airport.gate_queue[f1.from_gate])
