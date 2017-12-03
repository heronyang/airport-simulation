import sys
import logging

import conflict_tracker
from copy import deepcopy
from clock import Clock, ClockException
from airport import AirportFactory
from scenario import ScenarioFactory
from routing_expert import RoutingExpert
from scheduler import Scheduler
from analyst import Analyst
from utils import get_seconds_after, get_seconds_before
from uncertainty import Uncertainty
from config import Config
import numpy as np

class Simulation:

    def __init__(self, airport_code, sim_time, reschedule_time, uncertainty, tightness):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        # Sets up the sim_time for the simulation, it's a static variable of
        # `Clock` class
        Clock.sim_time = sim_time
        self.clock = Clock()

        # check for uncertainty
        if uncertainty:
            self.uncertainty = Uncertainty(uncertainty)
            ucrange = Config.UNCERTAINTY_RANGE_THRESHOLD * np.random.random_sample((2, ))
            uc_min = max(0, uncertainty - ucrange[0])
            uc_max = min(1, uncertainty + ucrange[1])
            self.uc_range = (uc_min, uc_max)
        else:
            self.uncertainty = None
            self.uc_range = None

        # Sets up the airport
        self.airport = AirportFactory.create(airport_code)

        # Sets up the scenario where scenario is mutable and base_scenario
        # isn't
        self.scenario = ScenarioFactory.create(airport_code,
                                               self.airport.surface)
        self.base_scenario = deepcopy(self.scenario)

        # Sets up the routing expert monitoring the airport surface
        self.routing_expert = RoutingExpert(self.airport.surface.links,
                                            self.airport.surface.nodes, False)
        self.scheduler = Scheduler()
        self.analyst = Analyst()

        # Sets up a delegate of this simulation
        self.delegate = SimulationDelegate(self)

        # Initializes the previous schedule time
        self.reschedule_time = reschedule_time
        self.last_schedule_time = None

        self.tightness = tightness

        self.print_stats()

    def tick(self):

        self.logger.debug("Current Time: %s" % self.now)

        try:
            self.add_aircraft_based_on_scenario()
            self.remove_aircraft_if_needed()
            self.reschedule_if_needed()
            self.analyst.observe_per_tick(self.delegate)

            self.airport.tick(self.uncertainty, self.scenario)
            self.logger.debug("No of conflicts found: %d",
                              conflict_tracker.conflicts_size())
            self.clock.tick()
        except ClockException as e:
            self.analyst.print_summary(self)
            raise e

    def quiet_tick(self):
        """
        Turn off the logger, reschedule, and analyst.
        """
        self.add_aircraft_based_on_scenario()
        self.remove_aircraft_if_needed()

        self.airport.tick(self.uncertainty, self.scenario)
        try:
            self.clock.tick()
        except ClockException as e:
            raise e

    def reschedule_if_needed(self):

        last_time = self.last_schedule_time
        next_time = get_seconds_after(last_time, self.reschedule_time) \
                if last_time is not None else None

        if last_time is None or next_time <= self.now:
            new_schedule = self.scheduler.schedule(self.delegate, self.now, self.tightness, self.uc_range)
            self.apply_schedule(new_schedule)
            self.last_schedule_time = self.now

    def apply_schedule(self, schedule):

        self.airport.apply_schedule(schedule)

        # Updates the delayed aircrafts into the scenario
        for (aircraft, time) in schedule.delayed_aircrafts:
            for flight in self.scenario.departures:
                if flight.aircraft == aircraft:
                    flight.appear_time = \
                            get_seconds_before(time, Config.APPEAR_BEFORE_TIME)
                    flight.departure_time = time

            for flight in self.scenario.arrivals:
                if flight.aircraft == aircraft:
                    flight.appear_time = \
                            get_seconds_before(time, Config.APPEAR_BEFORE_TIME)
                    flight.arrival_time = time

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

    def remove_aircraft_if_needed(self):
        """
        Removes departure aircrafts if they've moved to the runway.
        """
        # TODO: removal for arrival aircrafts
        for aircraft in self.airport.aircrafts:
            flight = self.scenario.get_flight(aircraft)
            if aircraft.location.is_close_to(flight.runway.start):
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
        self.uncertainty = None

    @property
    def airport(self):
        # TODO: should make it immutable before returning the airport state
        return self.simulation.airport

    @property
    def scenario(self):
        return self.simulation.scenario
    
    @property
    def reschedule_time(self):
        return self.simulation.reschedule_time
    @property
    def routing_expert(self):
        return self.simulation.routing_expert

    def set_uncertainty(self, uc):
        self.uncertainty = Uncertainty(uc)

    def predict_state_after(self, scheule, time_from_now):
        """
        Returns the simulation state and conflicts after `time_from_now`
        seconds.
        """
        simulation_copy = deepcopy(self.simulation)
        simulation_copy.uncertainty = self.uncertainty
        simulation.set_quiet(logger.getLogger("QUIET_MODE"))
        conflict_tracker.save_and_reset_conflicts()
        freezed_time = Clock.now
        for i in range(time_from_now / Clock.sim_time):
            simulation_copy.quiet_tick()
        conflicts = conflict_tracker.conflicts
        conflict_tracker.restore_conflicts()
        Clock.now = freezed_time
        return simulation_copy, conflicts
