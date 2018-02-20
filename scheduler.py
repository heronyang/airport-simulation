import logging

from schedule import Schedule
from aircraft import Aircraft, State
from route import Route
from itinerary import Itinerary
from config import Config
from utils import get_seconds_after, get_seconds, get_seconds_taken
from heapdict import heapdict

class Scheduler:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def schedule(self, simulation):

        self.logger.info("Scheduling start")
        last_occupied_time = {}

        # Sorts the flights by its departure or arrival time (prioirty queue)
        h = heapdict()
        for aircraft in simulation.airport.aircrafts:

            # Ignores the aircrafts contain itinerary requests
            if aircraft.pilot.itinerary is not None:
                continue

            # TODO: adds for arrivals
            flight = simulation.scenario.get_flight(aircraft)
            h[aircraft] = flight.departure_time

        requests = []
        while len(h) is not 0:
            aircraft, _ = h.popitem()
            itinerary = self.schedule_aircraft(aircraft,
                                               simulation, last_occupied_time)
            requests.append(Schedule.Request(aircraft, itinerary))

        self.logger.info("Scheduling end")
        return Schedule(requests, [], 0.0)

    def schedule_aircraft(self, aircraft, simulation, last_occupied_time):

        # Retrieves the route from the routing export
        flight = simulation.scenario.get_flight(aircraft)
        src = aircraft.location
        dst = flight.runway.start
        route = simulation.routing_expert.get_shortest_route(src, dst)

        start_time = flight.departure_time
        target_nodes = self.build_target_nodes(route, simulation.now,
                                               start_time, last_occupied_time)
        return Itinerary(target_nodes)

    def build_target_nodes(self, route, now, start_time, last_occupied_time):

        # Retrieves expected tightness value from the config file
        ps = Config.params["scheduler"]
        tightness = ps["tightness"]
        velocity = ps["aircraft_velocity"]

        target_nodes = []

        prev_node = None
        for node in route.nodes:

            # Gets the earliest available time of the node
            earliest_available_time = last_occupied_time.get(node, now)

            # Gets the earliest arrival time that the aircraft can make
            moving_time = get_seconds_taken(prev_node, node, velocity) \
                    if prev_node else 0
            earliest_arr_time = get_seconds_after(start_time, moving_time)

            # Sets the arrival time of the node in itinerary
            arr_time = max(earliest_available_time, earliest_arr_time)
            dep_time = arr_time
            target_nodes.append(Itinerary.TargetNode(node, arr_time, dep_time))

            # Marks
            prev_node = node
            last_occupied_time[node] = dep_time

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)

class DelayedException(Exception):
    pass
