from utils import get_seconds_after
from datetime import time

"""
Each time tick is excuted representing that `sim_time` has passed in the
simulated world.
"""
class Clock:

    def __init__(self, sim_time):

        # Starts at 00:00
        self.time = time(0, 0)

        # Step
        self.sim_time = sim_time

    def tick(self):

        time_after_tick = get_seconds_after(self.time, self.sim_time)

        if time_after_tick < self.time:
            raise ClockException("Reached the end of the day")

        self.time = time_after_tick

    @property
    def now(self):
        return self.time

class ClockException(Exception):
    pass
