from utils import get_seconds_after
from datetime import time

"""
Each time tick is excuted representing that `sim_time` has passed in the
simulated world.
"""
class Clock:

    # sim_time is a static variable that can be used anywhere
    sim_time = None
    now = None

    def __init__(self):

        # Starts at 00:00
        Clock.now = time(0, 0)

    def tick(self):

        time_after_tick = get_seconds_after(Clock.now, self.sim_time)

        if time_after_tick < Clock.now:
            raise ClockException("Reached the end of the day")

        Clock.now = time_after_tick

class ClockException(Exception):
    pass
