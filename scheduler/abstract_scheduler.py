import logging

from copy import deepcopy
from itinerary import Itinerary


class AbstractScheduler:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def schedule(self, simulation):
        raise NotImplementedError("Schedule function should be overrided.")

    def schedule_aircraft(self, aircraft, simulation):

        # Retrieves the route from the routing export
        flight = simulation.scenario.get_flight(aircraft)
        src, dst = aircraft.location, flight.runway.start
        route = simulation.routing_expert.get_shortest_route(src, dst)

        itinerary = Itinerary(deepcopy(route.nodes))

        # Aggregates the uncertainty delay in previous itinerary if found
        if aircraft.itinerary:
            n_uncertainty_delay = aircraft.itinerary.n_future_uncertainty_delay
            itinerary.add_uncertainty_delay(n_uncertainty_delay)

        return itinerary

    def __getstate__(self):
        attrs = dict(self.__dict__)
        del attrs["logger"]
        return attrs

    def __setstate__(self, attrs):
        self.__dict__.update(attrs)
