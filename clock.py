from utils import get_seconds_after
from datetime import time
from config import Config


class Clock:

    def __init__(self):

        # Starts at 00:00
        self.now = time(0, 0)
        self.sim_time = Config.params["simulation"]["time_unit"]

    def tick(self):

        time_after_tick = get_seconds_after(self.now, self.sim_time)

        if time_after_tick < self.now:
            raise ClockException("End of the day")

        self.now = time_after_tick

    def __repr__(self):
        return "<Clock: %s>" % self.now


class ClockException(Exception):
    pass
