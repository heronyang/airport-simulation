import logging
from schedule import Schedule

class Scheduler:

    def __init__(self):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

    def schedule(self, simulation, time):
        # simulation.airport : all airport states
        # simulation.routing_expert : gets rounts from node A to node B
        # time : time of a day
        self.logger.debug("Scheduling starts")
        self.logger.debug("Found %d aircrafts", len(simulation.airport.aircrafts))

        # helper function:
        # conflicts = simulation.predict_state_after(schedule, time_from_now)

        # Excepted return: schedule
        self.logger.debug("Scheduling done")
        return Schedule({})
