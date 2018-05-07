import random
import logging
from config import Config
from surface import Gate, Spot


class Uncertainty:

    def __init__(self, prob_hold):
        self.logger = logging.getLogger(__name__)
        self.prob_hold = prob_hold

    def inject(self, simulation):

        def __is_gate(aircraft):
            return (
                Config.params["uncertainty"]["at_gate"] and
                isinstance(aircraft.location, Gate)
            )

        def __is_spot(aircraft):
            return (
                Config.params["uncertainty"]["at_spot"] and
                isinstance(aircraft.location, Spot)
            )

        def __is_runway(aircraft):
            return (
                Config.params["uncertainty"]["at_runway"] and
                aircraft.next_location.is_close_to(runway_start)
            )

        for aircraft in simulation.airport.aircrafts:

            # For each aircraft at Gate, there's a possibility it holds at the
            # node for some random amount of time.
            if not self.happens_with_prob(self.prob_hold):
                continue

            # If it's already be delayed, we don't inject delay again.
            if aircraft.itinerary.is_delayed_by_uncertainty_now:
                continue

            flight = simulation.scenario.get_flight(aircraft)
            runway_start = flight.runway.start

            if not (__is_gate(aircraft) or
                    __is_spot(aircraft) or
                    __is_runway(aircraft)):
                continue

            if aircraft.itinerary is not None:
                ticks_hold = Config.params["uncertainty"]["ticks_hold"]
                for _ in range(ticks_hold):
                    aircraft.add_uncertainty_delay()
                self.logger.info("%s added %d delay", aircraft, ticks_hold)

    def happens_with_prob(self, prob):
        return random.random() < prob
