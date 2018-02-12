import logging
from clock import Clock
from aircraft import State
from utils import get_time_delta
from copy import deepcopy

class Analyst:

    def __init__(self, scenario):

        # Setups the logger
        self.logger = logging.getLogger(__name__)
        self.aircraft_tick_while_moving_counter = 0

        self.first_aircraft_appear_time = None
        self.last_aircraft_remove_time = None

        self.base_scenario = deepcopy(scenario)

    def observe_per_tick(self, simulation):

        for aircraft in simulation.airport.aircrafts:
            # If an aircraft is not close to its gate, it's on its taxiway
            flight = simulation.scenario.get_flight(aircraft)
            if not aircraft.location.is_close_to(flight.from_gate):
                self.aircraft_tick_while_moving_counter += 1

        if self.first_aircraft_appear_time is None and \
           len(simulation.airport.aircrafts) != 0:
            self.first_aircraft_appear_time = Clock.now

        if self.first_aircraft_appear_time is not None and \
           self.last_aircraft_remove_time is None and \
           len(simulation.airport.aircrafts) == 0:
            self.last_aircraft_remove_time = Clock.now

    def print_summary(self, simulation):

        # Taxitime
        taxi_time = self.aircraft_tick_while_moving_counter * Clock.sim_time

        # Remaining aircrafts
        remaining_aircrafts = len(simulation.airport.aircrafts)

        # Maxspan
        if self.first_aircraft_appear_time is not None and \
           self.last_aircraft_remove_time is not None:
            maxspan = get_time_delta(self.last_aircraft_remove_time,
                                     self.first_aircraft_appear_time) * 1.0
        else:
            maxspan = float('Inf')

        # Delay
        delay = 0
        for flight_planned in self.base_scenario.arrivals:
            for flight_simulated in simulation.scenario.arrivals:
                delay += get_time_delta(flight_planned.arrival_time,
                                        flight_simulated.arrival_time)

        # Prints
        self.logger.debug("Total taxi-time: %d seconds" % taxi_time)
        self.logger.debug("Number of remainging aircrafts: %d" %
                          remaining_aircrafts)
        if remaining_aircrafts == 0:
            self.logger.debug("Last flight departed at: %s" %
                              str(self.last_aircraft_remove_time))
        self.logger.debug("Maxspan: %f seconds" % maxspan)
        self.logger.debug("Total delayed time: %d seconds", delay)

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
