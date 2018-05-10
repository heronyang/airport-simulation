"""`Clock` keeps the simulated time of the simulation and it raises a
`ClockException` if it's the end of the day.
"""
from datetime import time
from config import Config
from utils import get_seconds_after


class Clock:
    """`Clock` simulates the the virtual time used in the simulation."""

    def __init__(self):

        # Starts at 00:00
        self.now = time(0, 0)
        self.sim_time = Config.params["simulation"]["time_unit"]
        end_time_raw = Config.params["simulation"]["end_time"].split(":")
        self.end_time = time(int(end_time_raw[0]), int(end_time_raw[1]))

    def tick(self):
        """Moves the clock to next tick."""

        time_after_tick = get_seconds_after(self.now, self.sim_time)
        if time_after_tick > self.end_time:
            raise ClockException("End of the day")
        self.now = time_after_tick

    def __repr__(self):
        return "<Clock: %s>" % self.now


class ClockException(Exception):
    """`ClockException` is used when the `Clock` object hits an exception."""
    pass
