import os

from surface import SurfaceFactory
from schedule import ScheduleFactory
from IPython.core.debugger import Tracer

class Airport:
    """
    Airport contains the surface, the arrival/departure schedule, and all the
    aircrafts currently moving or parking in this airport. The flight data in
    `schedule` is for lookups while the `aircraft` list represents the real
    aircrafts in the airport.
    """

    # Static data
    code = None
    surface = None

    # Read only data
    schedule = None

    # Runtime data
    aircrafts = []

    def __init__(self, code, surface, schedule):
        self.code = code
        self.surface = surface
        self.schedule = schedule

class AirportFactory:

    DATA_ROOT_DIR_PATH = "./data/%s/build/"

    @classmethod
    def create(self, code):

        dir_path = AirportFactory.DATA_ROOT_DIR_PATH % code

        # Checks if the folder exists
        if not os.path.exists(dir_path):
            raise Exception("Surface data is not ready")

        surface = SurfaceFactory.create(dir_path)
        schedule = ScheduleFactory.create(dir_path)

        return Airport(code, surface, schedule)
