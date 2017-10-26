import os
import logging

from surface import SurfaceFactory
from scenario import ScenarioFactory

class Airport:
    """
    Airport contains the surface, the arrival/departure scenario, and all the
    aircrafts currently moving or parking in this airport. The flight data in
    `scenario` is for lookups while the `aircraft` list represents the real
    aircrafts in the airport.
    """

    def __init__(self, code, surface, scenario):

        # Runtime data
        self.aircrafts = []

        # Static data
        self.code = code
        self.surface = surface

        # Read only data
        self.scenario = scenario

        # Setups the logger
        self.logger = logging.getLogger(__name__)

    """
    Callback function for handling the scenario response. Adds target for an
    aircraft with its expected completion time.
    """
    def add_target(self, aircraft, target, expected_completion_time):
        route = route_expert.get_shortest_route(aircraft.location, target)
        aircraft.add_itinerary(Itinerary(route, expected_completion_time))

class AirportFactory:

    DATA_ROOT_DIR_PATH = "./data/%s/build/"

    @classmethod
    def create(self, code):

        dir_path = AirportFactory.DATA_ROOT_DIR_PATH % code

        # Checks if the folder exists
        if not os.path.exists(dir_path):
            raise Exception("Surface data is not ready")

        surface = SurfaceFactory.create(dir_path)
        scenario = ScenarioFactory.create(dir_path, surface)

        return Airport(code, surface, scenario)
