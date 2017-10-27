import logging

from schedule import Schedule
from aircraft import Aircraft
from route import Itinerary, Route

class Scheduler:

    def __init__(self):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

    def schedule(self, simulation, time):
        # simulation.airport : all airport states
        # simulation.routing_expert : gets rounts from node A to node B
        # time : time of a day
        self.logger.debug("Scheduling starts")
        self.logger.debug("Found %d aircrafts", len(simulation.airport.aircrafts))

        # helper function:
        # conflicts = simulation.predict_state_after(schedule, time_from_now)
        ai = {}
        for aircraft in simulation.airport.aircrafts:
            if aircraft.state == Aircraft.State.stopped:

                # Pull outs the flight information
                flight = simulation.airport.scenario.get_flight(aircraft)

                # Gets the route from the routing expert
                route = simulation.routing_expert.get_shortest_route(
                    flight.from_gate, flight.spot)
                ai[aircraft] = Itinerary(route, flight.departure_time)
                self.logger.debug("Adds route %s on %s" % (route, aircraft))

        # Excepted return: schedule
        self.logger.debug("Scheduling done")
        return Schedule(ai)
