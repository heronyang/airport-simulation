import logging

from schedule import Schedule
from aircraft import Aircraft, State
from route import Route
from itinerary import Itinerary
from config import Config
from utils import get_seconds_after, get_seconds, get_seconds_taken
from heapdict import heapdict


class AbstractScheduler:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.delay_time = Config.params["scheduler"]["delay_time"]

    def schedule(self, simulation):
        raise NotImplementedError("Schedule function should be overrided.")

    def schedule_aircraft(self, aircraft, simulation):

        # Retrieves the route from the routing export
        flight = simulation.scenario.get_flight(aircraft)
        src, dst = aircraft.location, flight.runway.start
        route = simulation.routing_expert.get_shortest_route(src, dst)

        return Itinerary(route.nodes)

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
