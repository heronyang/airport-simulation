import sys
import logging

import airport

from airport import AirportFactory
from routing_expert import RoutingExpert

class Simulation:

    def __init__(self, airport_code):

        # Sets up the airport
        self.airport = AirportFactory.create(airport_code)

        # Sets up the routing expert monitoring the airport surface
        self.routing_expert = RoutingExpert(self.airport.surface.links,
                                            self.airport.surface.nodes)

    def update(self):
        pass

    def close(self):
        pass

    def get_static_state(self):
        # TODO: incompleted
        return None

    def get_runtime_state(self):
        # TODO: incompleted
        return None
