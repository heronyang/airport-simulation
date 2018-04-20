import os
import logging
import itertools

from surface import SurfaceFactory
from config import Config
from conflict import Conflict


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
                    airport_aircraft.set_itinerary(itinerary)
                    is_applied = True
                    break
            if not is_applied:
                raise Exception("%s not found in the airport" % aircraft)

    def add_aircraft(self, aircraft):
        self.aircrafts.append(aircraft)

    def remove_aircraft(self, aircraft):
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
            __conflicts.append(Conflict((l0, l1), ap, self.simulation.now))
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


class AirportFactory:

    @classmethod
    def create(self, simulation, code):

        dir_path = Config.DATA_ROOT_DIR_PATH % code

        # Checks if the folder exists
        if not os.path.exists(dir_path):
            raise Exception("Surface data is missing")

        surface = SurfaceFactory.create(dir_path)
        return Airport(simulation, code, surface)
