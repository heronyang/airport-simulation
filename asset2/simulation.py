import sys
import logging

from clock import Clock
from airport import AirportFactory
from scenario import ScenarioFactory
from routing_expert import RoutingExpert
from scheduler import Scheduler
from utils import get_seconds_after

class Simulation:

    def __init__(self, airport_code, sim_time, reschedule_time):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        # Sets up the clock used in the simulation
        self.clock = Clock(sim_time)

        # Sets up the airport
        self.airport = AirportFactory.create(airport_code)

        # Sets up the scenario
        self.scenario = ScenarioFactory.create(airport_code,
                                               self.airport.surface)

        # Sets up the routing expert monitoring the airport surface
        self.routing_expert = RoutingExpert(self.airport.surface.links,
                                            self.airport.surface.nodes)
        self.scheduler = Scheduler()

        # Sets up a delegate of this simulation
        self.delegate = SimulationDelegate(self)

        # Initializes the previous schedule time
        self.reschedule_time = reschedule_time
        self.last_schedule_time = None

        self.print_stats()

    def tick(self):

        self.logger.debug("Current Time: %s" % self.now)

        self.add_aircraft_based_on_scenario()
        self.reschedule_if_needed()

        self.airport.tick()
        self.clock.tick()

    def reschedule_if_needed(self):

        last_time = self.last_schedule_time
        next_time = get_seconds_after(last_time, self.reschedule_time) \
                if last_time is not None else None

        if last_time is None or next_time <= self.now:
            new_schedule = self.scheduler.schedule(self.delegate, self.now)
            self.apply_schedule(new_schedule)
            self.last_schedule_time = self.now

    def apply_schedule(self, schedule):
        self.airport.apply_schedule(schedule)

    def add_aircraft_based_on_scenario(self):

        # NOTE: we will only focus on departures now

        next_tick_time = get_seconds_after(self.now, self.clock.sim_time)

        # For all departure flights
        for flight in self.scenario.departures:
            # If it the scheduled appear time is between now and next tick time
            if self.now <= flight.appear_time and \
               flight.appear_time < next_tick_time:

                self.logger.debug("Adds flight %s to the airport" % flight)

                # Adds the flight to the airport
                flight.aircraft.set_location(flight.from_gate)
                self.airport.add_aircraft(flight.aircraft)

    @property
    def now(self):
        return self.clock.now

    def print_stats(self):

        self.scenario.print_stats()
        self.airport.print_stats()


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

    def predict_state_after(self, scheule, time_from_now):
        # TODO
        # 1. copy the current airport state
        # 2. tick() on the airport
        # 3. return the copied airport state
        airport = None
        conflicts = []
        return (airport, conflicts)
