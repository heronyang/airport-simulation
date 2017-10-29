import logging
from clock import Clock
from aircraft import State

class Analyst:

    def __init__(self):

        # Setups the logger
        self.logger = logging.getLogger(__name__)
        self.aircraft_tick_while_moving_counter = 0

    def observe_per_tick(self, simulation):

        # Accumulate the number of ticks happened while aircraft is moving
        for aircraft in simulation.airport.aircrafts:
            if aircraft.state == State.moving:
                self.aircraft_tick_while_moving_counter += 1

    def print_summary(self):
        taxi_time = self.aircraft_tick_while_moving_counter * Clock.sim_time
        self.logger.debug("Total taxi-time: %d seconds" % taxi_time)
