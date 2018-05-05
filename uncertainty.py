import random
import logging
from surface import Gate, Spot


class Uncertainty:

    def __init__(self, prob_hold):
        self.logger = logging.getLogger(__name__)
        self.prob_hold = prob_hold

    def inject(self, simulation):

        for aircraft in simulation.airport.aircrafts:

            # For each aircraft at Gate, there's a possibility it holds at the
            # node for some random amount of time.

            if not self.happens_with_prob(self.prob_hold):
                continue

            if type(aircraft.location) is not Gate and\
               type(aircraft.location) is not Spot:
                continue

            if aircraft.itinerary is not None:
                aircraft.add_uncertainty_delay()
                self.logger.info("%s added delay" % aircraft)

    def happens_with_prob(self, prob):
        return random.random() < prob
