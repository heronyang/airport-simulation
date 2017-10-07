from datetime import date, datetime, time, timedelta

"""In simulation, every SIM_SECOND seconds represents REAL_MINUTE minutes in
real world. And, every SIM_SECOND seconds in simulation (or REAL_MINUTE
minutes in real world) the simluation sends a request to schedule for a new
schedule.
"""

SIM_SECOND = 1
REAL_MINUTE = 15

class Clock:

    def __init__(self):

        # Starts at 00:00
        self.time = time(0, 0)

        # Step
        self.step = timedelta(minutes = REAL_MINUTE)

    def tick(self):

        # Since time calculation only works on datetime (not time), so we first
        # combine with today, then get the time() part
        self.time = (datetime.combine(date.today(), self.time) + self.step).time()

    def now(self):
        return self.time

    def get_sim_step_second():
        return SIM_SECOND
