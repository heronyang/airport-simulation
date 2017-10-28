import logging

from schedule import Schedule
from aircraft import Aircraft
from route import Route
from itinerary import Itinerary

class Scheduler:

    def __init__(self):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

    def schedule(self, simulation, time):

        # simulation.airport : all airport states
        # simulation.routing_expert : gets routes from node A to node B
        # time : current simulated time of a day
        self.logger.debug("Scheduling starts")
        self.logger.debug("Found %d aircrafts",
                          len(simulation.airport.aircrafts))

        # helper function:
        # conflicts = simulation.predict_state_after(schedule, time_from_now)

        # put break point:
        # from IPython.core.debugger import Tracer; Tracer()()

        requests = []
        for aircraft in simulation.airport.aircrafts:
            if aircraft.state == Aircraft.State.stopped:

                # Pull outs the flight information
                flight = simulation.scenario.get_flight(aircraft)

                # Gets the route from the routing expert
                route = simulation.routing_expert.get_shortest_route(
                    flight.from_gate, flight.spot)

                itinerary = Itinerary(route, flight.departure_time)
                requests.append(Schedule.Request(aircraft, itinerary))
                self.logger.debug("Adds route %s on %s" % (route, aircraft))

        self.logger.debug("Scheduling done")
        return Schedule(requests)
