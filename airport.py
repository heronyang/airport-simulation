import os
import logging
import itertools

from surface import SurfaceFactory
from config import Config
from conflict import Conflict
from aircraft import State
from node import get_middle_node
from copy import deepcopy


class Airport:
    """
    Airport contains the surface and all the aircrafts currently moving or
    stopped in this airport.
    """

    def __init__(self, simulation, code, surface):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        # Runtime data
        self.aircrafts = []

        # Pointer to the simulation
        self.simulation = simulation

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
                    airport_aircraft.set_itinerary(deepcopy(itinerary))
                    is_applied = True
                    break
            if not is_applied:
                raise Exception("%s not found in the airport" % r.aircraft)

    def add_aircraft(self, aircraft):
        self.aircrafts.append(aircraft)

    def remove_aircraft(self, aircraft):
        self.aircrafts.remove(aircraft)

    @property
    def conflicts(self):

        __conflicts = []
        aircraft_pairs = list(itertools.combinations(self.aircrafts, 2))
        for ap in aircraft_pairs:
            l0, l1 = ap[0].location, ap[1].location
            if not l0 == l1:
                continue
            __conflicts.append(Conflict(l0, ap, self.simulation.now))
        return __conflicts

    def is_occupied_at(self, node):
        for aircraft in self.aircrafts:
            if node == aircraft.location:
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


class AirportFactory:

    @classmethod
    def create(self, simulation, code):

        dir_path = Config.DATA_ROOT_DIR_PATH % code

        # Checks if the folder exists
        if not os.path.exists(dir_path):
            raise Exception("Surface data is missing")

        surface = SurfaceFactory.create(dir_path)
        return Airport(simulation, code, surface)
