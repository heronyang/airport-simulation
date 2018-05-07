import random
import logging
from config import Config
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

            """
            if type(aircraft.location) is not Gate and\
               type(aircraft.location) is not Spot:
                continue
            """

            # Uncertainty delays are added at the runway start
            flight = simulation.scenario.get_flight(aircraft)
            runway_start = flight.runway.start
            if not aircraft.location.is_close_to(runway_start):
                continue

            if aircraft.itinerary is not None:
                ticks_hold = Config.params["uncertainty"]["ticks_hold"]
                for _ in range(ticks_hold):
                    aircraft.add_uncertainty_delay()
                self.logger.info("%s added %d delay" % (aircraft, ticks_hold))

    def happens_with_prob(self, prob):
        return random.random() < prob
