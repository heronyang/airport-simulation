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

    def schedule(self, simulation):
        raise NotImplementedError("Schedule function should be overrided.")

    def schedule_aircraft(self, aircraft, simulation, last_occupied_time=None):

        # Retrieves the route from the routing export
        flight = simulation.scenario.get_flight(aircraft)
        src = aircraft.location
        dst = flight.runway.start
        departure_time = flight.departure_time
        now = simulation.now
        route = simulation.routing_expert.get_shortest_route(src, dst)
        true_location = aircraft.true_location

        # Prepend its current location to targets if the location isn't true
        if aircraft.state is not State.moving:
            true_location = None

        # Start time is the later time between departure time and now
        start_time = departure_time if departure_time > now else now

        targets = self.build_targets(route, start_time,
                                     last_occupied_time=last_occupied_time,
                                     true_location=true_location)
        return Itinerary(targets)

    # If last_occupied_time is not given, we ignore tightness enforcement.
    def build_targets(self, route, start_time, last_occupied_time=None,
                      true_location=True):

        ps = Config.params["scheduler"]
        velocity = ps["aircraft_velocity"]

        if last_occupied_time is not None:
            # Retrieves expected tightness value from the config file
            tightness = ps["tightness"]

        targets = []

        prev_node, prev_time = None, start_time

        nodes = [true_location] + route.nodes if true_location else route.nodes
        for node in nodes:

            # Gets the earliest available time of the node
            if last_occupied_time is not None:
                earliest_available_time = (
                    get_seconds_after(last_occupied_time[node], tightness)
                    if node in last_occupied_time else prev_time
                )
            else:
                earliest_available_time = prev_time

            # Gets the earliest arrival time that the aircraft can make
            moving_time = (get_seconds_taken(prev_node, node, velocity)
                           if prev_node else 0)
            earliest_arr_time = get_seconds_after(prev_time, moving_time)

            # Sets the arrival time of the node in itinerary
            arr_time = max(earliest_available_time, earliest_arr_time)
            dep_time = arr_time
            targets.append(Itinerary.Target(node, arr_time, dep_time))

            # Marks
            prev_node, prev_time = node, dep_time

            if last_occupied_time is not None:
                last_occupied_time[node] = dep_time

        return targets

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
