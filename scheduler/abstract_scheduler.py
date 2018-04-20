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
        # NOTE: At the time an aircraft appears is the planned departure time,
        # so we don't have to add delays at gate for waiting until depature.
        flight = simulation.scenario.get_flight(aircraft)
        src, dst = aircraft.location, flight.runway.start
        route = simulation.routing_expert.get_shortest_route(src, dst)

        return Itinerary(deepcopy(route.nodes))

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
