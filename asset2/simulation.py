import sys
import logging

from clock import Clock
from airport import AirportFactory
from routing_expert import RoutingExpert

class Simulation:

    def __init__(self, airport_code, sim_time, schedule_time):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        # Sets up the clock used in the simulation
        self.clock = Clock(sim_time)

        # Sets up the airport
        self.airport = AirportFactory.create(airport_code)

        # Sets up the routing expert monitoring the airport surface
        # self.routing_expert = RoutingExpert(self.airport.surface.links,
                                            # self.airport.surface.nodes)

        # Sets up a delegate of this simulation
        self.delegate = SimulationDelegate(self)

    def tick(self):
        # TODO
        self.clock.tick()
        self.logger.debug("Current Time: %s" % self.clock.now)

    def close(self):
        self.logger("Closing the simulation")

class SimulationDelegate:
    """
    SimulationDelegate is used for scheduler to access simulation state without
    breaking on-going things or creating deadlocks.
    """

    def __init__(self, simulation):
        self.simulation = simulation

    @property
    def airport(self):
        return self.simulation.airport.copy()

    @property
    def routing_expert(self):
        return self.simulation.routing_expert

    def predict_state_after(self, scheule, time_from_now):
        # TODO
        airport = None
        conflicts = []
        return (airport, conflicts)
