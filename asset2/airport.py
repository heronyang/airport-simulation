import os
import logging

from surface import SurfaceFactory
from scenario import ScenarioFactory
from config import Config

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
            r.aircraft.add_itinerary(r.itinerary)

    def add_aircraft(self, aircraft):
        self.aircrafts.append(aircraft)

    def tick(self):
        for aircraft in self.aircrafts:
            aircraft.pilot.tick()

    def print_stats(self):

        # Prints surface stats
        self.surface.print_stats()

class AirportFactory:

    @classmethod
    def create(self, code):

        dir_path = Config.DATA_ROOT_DIR_PATH % code

        # Checks if the folder exists
        if not os.path.exists(dir_path):
            raise Exception("Surface data is not ready")

        surface = SurfaceFactory.create(dir_path)
        return Airport(code, surface)
