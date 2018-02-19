import sys
import logging

from copy import deepcopy
from clock import Clock, ClockException
from airport import AirportFactory
from scenario import ScenarioFactory
from routing_expert import RoutingExpert
from scheduler import Scheduler
from analyst import Analyst
from utils import get_seconds_after, get_seconds_before
from uncertainty import Uncertainty
from conflict import Conflict, ConflictTracker
from config import Config
import numpy as np

class Simulation:

    def __init__(self):

        p = Config.params

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        # Setups the clock
        self.clock = Clock()

        # Sets up the airport
        airport_code = p["airport"]
        self.airport = AirportFactory.create(self, airport_code)

        # Sets up the scenario
        self.scenario = ScenarioFactory.create(self, airport_code,
                                               self.airport.surface)

        # Sets up the routing expert monitoring the airport surface
        self.routing_expert = RoutingExpert(self.airport.surface.links,
                                            self.airport.surface.nodes, False)

        # check for uncertainty
        self.uncertainty = Uncertainty() \
                if p["uncertainty"]["enabled"] else None

        self.scheduler = Scheduler()
        self.analyst = Analyst(self.scenario)
        self.conflict_tracker = ConflictTracker()

        # Sets up a delegate of this simulation
        self.delegate = SimulationDelegate(self)

        # Initializes the previous schedule time
        self.last_schedule_time = None
        self.print_stats()

    def tick(self):

        self.logger.info("Current Time: %s" % self.now)

        try:

            # Updates states
            # from IPython.core.debugger import Tracer; Tracer()()
            self.update_aircrafts()
            if self.is_time_to_reschedule():
                self.logger.info("Time to reschedule")
                # self.reschedule()
                self.last_schedule_time = self.now
                self.logger.debug("Last schedule time is updated to %s" %
                                  self.last_schedule_time)
            # self.airport.tick(self.uncertainty, self.scenario)
            self.clock.tick()

            # Observe
            # self.analyst.observe_per_tick(self.delegate)

        except ClockException as e:

            # Finishes
            self.analyst.print_summary(self)
            raise e

    def update_aircrafts(self):
        self.add_aircrafts()
        self.remove_aircrafts()

    def quiet_tick(self):
        """
        Turn off the logger, reschedule, and analyst.
        """
        self.add_aircrafts()
        self.remove_aircrafts()

        self.airport.tick()
        try:
            self.clock.tick()
        except ClockException as e:
            raise e

    def is_time_to_reschedule(self):
        reschedule_cycle = Config.params["simulation"]["reschedule_cycle"]
        last_time = self.last_schedule_time
        next_time = get_seconds_after(last_time, reschedule_cycle) \
                if last_time is not None else None
        return last_time is None or next_time <= self.now

    def reschedule(self):
        schedule = self.scheduler.schedule(self.delegate, self.now,
                                           self.uncertainty.range)
        self.apply_schedule(schedule)

    def apply_schedule(self, schedule):

        self.airport.apply_schedule(schedule)

        # Updates the delayed aircrafts into the scenario
        appear_before = Config.params["simulation"]["appear_before"]
        for (aircraft, time) in schedule.delayed_aircrafts:

            for flight in self.scenario.departures:
                if flight.aircraft == aircraft:
                    flight.appear_time = get_seconds_before(time, appear_before)
                    flight.departure_time = time

            for flight in self.scenario.arrivals:
                if flight.aircraft == aircraft:
                    flight.appear_time = get_seconds_before(time, appear_before)
                    flight.arrival_time = time

    def add_aircrafts(self):

        # NOTE: we will only focus on departures now
        next_tick_time = get_seconds_after(self.now, self.clock.sim_time)

        # For all departure flights
        for flight in self.scenario.departures:
            # If it the scheduled appear time is between now and next tick time
            if self.now <= flight.appear_time and \
               flight.appear_time < next_tick_time:

                self.logger.info("Adds %s into the airport" % flight)

                # Adds the flight to the airport
                flight.aircraft.set_location(flight.from_gate)
                self.airport.add_aircraft(flight.aircraft)

    def remove_aircrafts(self):
        """
        Removes departure aircrafts if they've moved to the runway.
        """
        # TODO: removal for arrival aircrafts
        for aircraft in self.airport.aircrafts:
            flight = self.scenario.get_flight(aircraft)
            if aircraft.location.is_close_to(flight.runway.start):
                self.logger.info("Removes %s from the airport" % flight)
                self.airport.remove_aircraft(aircraft)

    @property
    def now(self):
        return self.clock.now

    def print_stats(self):
        self.scenario.print_stats()
        self.airport.print_stats()

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)

    def set_quiet(self, logger):
        self.logger = logger
        self.airport.set_quiet(logger)
        self.scenario.set_quiet(logger)
        self.routing_expert.set_quiet(logger)

class SimulationDelegate:
    """
    SimulationDelegate is used for scheduler to access simulation state without
    breaking on-going things or creating deadlocks.
    """

    def __init__(self, simulation):
        self.simulation = simulation

    @property
    def airport(self):
        # TODO: should make it immutable before returning the airport state
        return self.simulation.airport

    @property
    def scenario(self):
        return self.simulation.scenario

    @property
    def routing_expert(self):
        return self.simulation.routing_expert

    def predict_state_after(self, scheule, time_from_now, uncertainty):
        """
        Returns the simulation state after `time_from_now` seconds.
        """

        # Gets a snapshot of current simulation state
        simulation_copy = deepcopy(self.simulation)

        # Replace the uncertainty module by the given one
        simulation_copy.uncertainty = uncertainty

        # Replace the conflict tracker with a new one
        simulation_copy.conflict_tracker = ConflictTracker()

        # Sets the simulation to quiet mode
        simulation_copy.set_quiet(logger.getLogger("QUIET_MODE"))

        # Applies the schedule
        simulation_copy.apply_schedule(scheule)

        # Starts to simulate the future state
        for i in range(time_from_now / simultion_copy.clock.sim_time):
            simulation_copy.quiet_tick()

        return simulation_copy
