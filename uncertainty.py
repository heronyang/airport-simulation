import os
import random
from config import Config


class Uncertainty:

    def __init__(
        self,
        prob_hold=Config.params["uncertainty"]["prob_hold"],
        hold_time_mean=Config.params["uncertainty"]["hold_time_mean"],
        hold_time_deviation=Config.params["uncertainty"]["hold_time_deviation"]
    ):
        self.prob_hold = prob_hold
        self.hold_time_mean = hold_time_mean
        self.hold_time_deviation = hold_time_deviation

    def inject(self, simulation):

        for aircraft in simulation.airport.aircrafts:
            # For each aircraft, there's a possibility it holds at the node for
            # some random amount of time.
            if not self.happens_with_prob(self.prob_hold):
                continue

            delay = self.get_sample(self.hold_time_mean,
                                    self.hold_time_deviation)
            if delay <= 0:
                continue

            if aircraft.pilot.itinerary is not None:
                aircraft.pilot.itinerary.add_delay(delay)

    def happens_with_prob(self, prob):
        return random.random() < prob

    def get_sample(self, mean, deviation):
        return random.normalvariate(mean, deviation)
