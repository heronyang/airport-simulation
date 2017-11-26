import os
import logging
import itertools

from surface import SurfaceFactory
from scenario import ScenarioFactory
from config import Config
from clock import Clock
from conflict_tracker import add_conflict, Conflict

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

        # Static data
        self.code = code
        self.surface = surface

    def apply_schedule(self, schedule):
        for r in schedule.requests:
            if not r.aircraft in self.aircrafts:
                raise Exception("%s not found in the airport" % r.aircraft)
            r.aircraft.set_itinerary(r.itinerary)

    def add_aircraft(self, aircraft):
        self.aircrafts.append(aircraft)

    def remove_aircraft(self, aircraft):
        self.aircrafts.remove(aircraft)

    def log_conflicts(self):
        aircraft_pairs = list(itertools.combinations(self.aircrafts, 2))
        for ap in aircraft_pairs:
            if ap[0].location.is_close_to(ap[1].location):
                conflict = Conflict(ap, ap[0].location, Clock.now)
                self.logger.debug("Conflict found******************************** : %s at location %s at time %s ", ap, ap[0].location, Clock.now)
                add_conflict(conflict)

    def tick(self, uc, scenario):
        for aircraft in self.aircrafts:
            aircraft.pilot.tick(uc, scenario.get_flight(aircraft))
        self.log_conflicts()

    def print_stats(self):
        # Prints surface stats
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
            raise Exception("Surface data is not ready")

        surface = SurfaceFactory.create(dir_path)
        return Airport(code, surface)
