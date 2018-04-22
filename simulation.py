"""`Simulation` represents an airport simulation of a day on the given
parameters. `SimulationDelegate` is designed to be an immutable delegate of a
simultion that can be used for other objects to observe the simulation states.
"""
import time
import logging
import traceback
import importlib

from copy import deepcopy
from clock import Clock, ClockException
from airport import AirportFactory
from scenario import ScenarioFactory
from routing_expert import RoutingExpert
from analyst import Analyst
from utils import get_seconds_after
from uncertainty import Uncertainty
from config import Config
from state_logger import StateLogger


"""Simulation represents a simulation day, holds both static and dynamic states
of the current airport, and implements `tick()` and `quiet_tick()` functions
for the caller to simulation to the next state.
"""
class Simulation:

    def __init__(self):

        params = Config.params

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        # Setups the clock
        self.clock = Clock()

        # Sets up the airport
        airport_name = params["airport"]
        self.airport = AirportFactory.create(airport_name)

        # Sets up the scenario
        self.scenario = ScenarioFactory.create(
            airport_name, self.airport.surface)

        # Sets up the routing expert monitoring the airport surface
        self.routing_expert = RoutingExpert(self.airport.surface.links,
                                            self.airport.surface.nodes,
                                            params["simulation"]["cache"])

        # Sets up the uncertainty module
        self.uncertainty = (Uncertainty(params["uncertainty"]["prob_hold"])
                            if params["uncertainty"]["enabled"] else (None))

        # Loads the requested scheduler
        self.scheduler = get_scheduler()

        if not params["simulator"]["test_mode"]:

            # Sets up the analyst
            self.analyst = Analyst(self)

            # Sets up the state logger
            self.state_logger = StateLogger()

        # Initializes the previous schedule time
        self.last_schedule_time = None

        # Initializes the last execution time for rescheduling to None
        self.last_schedule_exec_time = None

        self.__print_stats()

    def tick(self):

        self.logger.debug("\nCurrent Time: %s" % self.now)

        try:
            # Reschedule happens before the tick
            if self.__is_time_to_reschedule():
                self.logger.info("Time to reschedule")
                start = time.time()
                self.__reschedule()
                self.last_schedule_exec_time = time.time() - start  # seconds
                self.last_schedule_time = self.now
                self.logger.info("Last schedule time is updated to %s" %
                                 self.last_schedule_time)

            # Injects uncertainties
            if self.uncertainty:
                self.uncertainty.inject(self)

            # Tick
            self.airport.add_aircrafts(self.scenario, self.now,
                                       self.clock.sim_time)
            self.airport.tick()
            if not Config.params["simulator"]["test_mode"]:
                self.state_logger.log_on_tick(self)
            self.airport.remove_aircrafts(self.scenario)
            self.clock.tick()

            # Abort on conflict
            if len(self.airport.conflicts) > 0:
                raise SimulationException("Conflict found")

            # Observe
            if not Config.params["simulator"]["test_mode"]:
                self.analyst.observe_on_tick(self)

        except ClockException as e:
            # Finishes
            if not Config.params["simulator"]["test_mode"]:
                self.analyst.save()
                self.state_logger.save()
            raise e
        except SimulationException as e:
            raise e
        except Exception as e:
            self.logger.error(traceback.format_exc())
            raise e

    def quiet_tick(self):
        """
        Turn off the logger, reschedule, and analyst.
        """
        self.logger.debug("\nPredicted Time: %s" % self.now)
        self.airport.add_aircrafts(self.scenario, self.now,
                                   self.clock.sim_time)
        self.airport.tick()
        self.airport.remove_aircrafts(self.scenario)
        try:
            self.clock.tick()
        except ClockException as e:
            raise e

    def __is_time_to_reschedule(self):
        reschedule_cycle = Config.params["simulation"]["reschedule_cycle"]
        last_time = self.last_schedule_time
        next_time = (get_seconds_after(last_time, reschedule_cycle)
                     if last_time is not None else None)
        return last_time is None or next_time <= self.now

    def __reschedule(self):
        schedule = self.scheduler.schedule(self)
        self.airport.apply_schedule(schedule)
        if not Config.params["simulator"]["test_mode"]:
            self.analyst.observe_on_reschedule(schedule, self)

    @property
    def now(self):
        return self.clock.now

    def __print_stats(self):
        self.scenario.print_stats()
        self.airport.print_stats()

    def __getstate__(self):
        __dict = dict(self.__dict__)
        del __dict["logger"]
        __dict["uncertainty"] = None
        __dict["routing_expert"] = None
        return __dict

    def __setstate__(self, new_dict):
        self.__dict__.update(new_dict)

    def set_quiet(self, logger):
        self.logger = logger
        self.airport.set_quiet(logger)
        self.scenario.set_quiet(logger)
        self.routing_expert.set_quiet(logger)

    @property
    def copy(self, uncertainty=None):
        # TODO: If uncertainty is not None, call inject() in quiet_tick().
        return ClonedSimulation(self)


class ClonedSimulation():

    def __init__(self, simulation):

        self.clock = deepcopy(simulation.clock)
        self.airport = deepcopy(simulation.airport)
        self.scenario = deepcopy(simulation.scenario)

        # Sets up the logger in quiet mode
        self.logger = logging.getLogger("QUIET_MODE")
        self.airport.set_quiet(self.logger)
        self.scenario.set_quiet(self.logger)

    def quiet_tick(self):
        """Turn off the logger, reschedule, and analyst.
        """
        self.logger.debug("\nPredicted Time: %s" % self.now)
        self.airport.add_aircrafts(self.scenario, self.now,
                                   self.clock.sim_time)
        self.airport.tick()
        self.airport.remove_aircrafts(self.scenario)
        try:
            self.clock.tick()
        except ClockException as e:
            raise e

    @property
    def now(self):
        return self.clock.now


def get_scheduler():
    # Loads the requested scheduler
    scheduler_name = Config.params["scheduler"]["name"]
    return importlib.import_module("scheduler." + scheduler_name).Scheduler()


class SimulationException(Exception):
    pass
