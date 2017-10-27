from datetime import date, datetime, time, timedelta

"""
Each time tick is excuted representing that `sim_time` has passed in the
simulated world.
"""
class Clock:

    def __init__(self, sim_time):

        # Starts at 00:00
        self.time = time(0, 0)

        # Step
        self.step = timedelta(seconds = sim_time)

    def tick(self):

        # Since time calculation only works on datetime (not time), so we first
        # combine self.time with today, then get the time() part
        holder = datetime.combine(date.today(), self.time)
        time_after_tick = (holder + self.step).time()

        if time_after_tick < self.time:
            raise ClockException("Reached the end of the day")

        self.time = time_after_tick

    @property
    def now(self):
        return self.time

class ClockException(Exception):
    pass
