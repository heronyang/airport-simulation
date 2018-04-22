import os
import logging
import itertools

from collections import deque
from surface import SurfaceFactory
from config import Config
from conflict import Conflict
from utils import get_seconds_after


class Airport:
    """
    Airport contains the surface and all the aircrafts currently moving or
    stopped in this airport.
    """

    def __init__(self, code, surface):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        # Runtime data
        self.aircrafts = []

        # Queues for departure flights at gates
        self.gate_queue = {}

        # Static data
        self.code = code
        self.surface = surface

    def apply_schedule(self, schedule):
        for aircraft, itinerary in schedule.itineraries.items():
            is_applied = False
            for airport_aircraft in self.aircrafts:
                if airport_aircraft == aircraft:
                    airport_aircraft.set_itinerary(itinerary)
                    is_applied = True
                    break
            if not is_applied:
                raise Exception("%s not found in the airport" % aircraft)

    def add_aircrafts(self, scenario, now, sim_time):
        self.__add_aircrafts_from_queue()
        self.__add_aircrafts_from_scenario(scenario, now, sim_time)

    def __add_aircrafts_from_queue(self):

        for gate, queue in self.gate_queue.items():

            if self.is_occupied_at(gate) or not queue:
                continue

            # Put the first aircraft in queue into the airport
            aircraft = queue.popleft()
            aircraft.set_location(gate)
            self.aircrafts.append(aircraft)

    def __add_aircrafts_from_scenario(self, scenario, now, sim_time):

        # NOTE: we will only focus on departures now
        next_tick_time = get_seconds_after(now, sim_time)

        # For all departure flights
        for flight in scenario.departures:

            # Only if the scheduled appear time is between now and next tick
            if not (now <= flight.appear_time and
                    flight.appear_time < next_tick_time):
                continue

            gate, aircraft = flight.from_gate, flight.aircraft

            if self.is_occupied_at(gate):
                # Adds the flight to queue
                queue = self.gate_queue.get(gate, deque())
                queue.append(aircraft)
                self.gate_queue[gate] = queue
                self.logger.info("Adds %s into gate queue" % flight)

            else:
                # Adds the flight to the airport
                aircraft.set_location(gate)
                self.aircrafts.append(aircraft)
                self.logger.info("Adds %s into the airport" % flight)

    def remove_aircrafts(self, scenario):
        """Removes departure aircrafts if they've moved to the runway.
        """

        to_remove_aircrafts = []

        for aircraft in self.aircrafts:
            flight = scenario.get_flight(aircraft)
            # Deletion shouldn't be done in the fly
            if aircraft.location.is_close_to(flight.runway.start):
                to_remove_aircrafts.append(aircraft)

        for aircraft in to_remove_aircrafts:
            self.logger.info("Removes %s from the airport" % aircraft)
            self.aircrafts.remove(aircraft)

    @property
    def conflicts(self):
        return self.__get_conflicts()

    @property
    def next_conflicts(self):
        return self.__get_conflicts(is_next=True)

    def __get_conflicts(self, is_next=False):
        __conflicts = []
        aircraft_pairs = list(itertools.combinations(self.aircrafts, 2))
        for ap in aircraft_pairs:
            if is_next:
                l0, l1 = ap[0].next_location, ap[1].next_location
            else:
                l0, l1 = ap[0].location, ap[1].location
            if not l0.is_close_to(l1):
                continue
            __conflicts.append(Conflict((l0, l1), ap))
        return __conflicts

    def is_occupied_at(self, node):
        for aircraft in self.aircrafts:
            if aircraft.location.is_close_to(node):
                return True
        return False

    def tick(self):
        for aircraft in self.aircrafts:
            aircraft.tick()

    def print_stats(self):
        self.surface.print_stats()

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)

    def set_quiet(self, logger):
        self.logger = logger
        self.surface.set_quiet(logger)
        for aircraft in self.aircrafts:
            aircraft.set_quiet(logger)


class AirportFactory:

    @classmethod
    def create(self, code):

        dir_path = Config.DATA_ROOT_DIR_PATH % code

        # Checks if the folder exists
        if not os.path.exists(dir_path):
            raise Exception("Surface data is missing")

        surface = SurfaceFactory.create(dir_path)
        return Airport(code, surface)
