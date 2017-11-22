import logging

from schedule import Schedule
from aircraft import Aircraft
from route import Route
from itinerary import Itinerary
from config import Config
from utils import get_seconds_after, get_seconds

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

            # Pulls outs the flight information
            flight = simulation.scenario.get_flight(aircraft)

            if aircraft.is_idle and \
               aircraft.location.is_close_to(flight.from_gate):

                # Gets the route from the routing expert
                # NOTE: We use runway start node as the destination of a
                # departure flight

                print(flight.from_gate, flight.runway.start) 
                route = simulation.routing_expert.get_shortest_route(
                    flight.from_gate, flight.runway.start)
                self.logger.debug("Get route: %s" % route)

                # Generates the itinerary for this aircraft
                target_nodes = []
                prev_node = None
                for node in route.nodes:
                    if prev_node is None:
                        arr_time = flight.departure_time
                    else:
                        arr_time = get_seconds_after(arr_time, self.get_delay(prev_node, node))

                    dep_time = arr_time

                    self.logger.debug("Route node is : %s, %s", node, get_seconds(arr_time))
                    target_nodes.append(
                        Itinerary.TargetNode(node, arr_time, dep_time))
                    
                    prev_node = node

                itinerary = Itinerary(target_nodes, flight.departure_time)
                requests.append(Schedule.Request(aircraft, itinerary))
                self.logger.debug("Adds route %s on %s" % (route, aircraft))


        conflictInfo = self.check_conflict(requests)

        # Repeatedly check for conflicts and resolve it until conflict-free schedule is obtained
        count = 0
        while conflictInfo is not None: 
            requests = self.resolve_conflict(conflictInfo, requests)
            conflictInfo = self.check_conflict(requests)
            count+=1
        
        self.logger.debug("Scheduling done")
        return Schedule(requests)

    def get_delay(self, start_node, end_node):
        """
         Return:
            -time required for the airpline to move from start node to destination node
        """

        return int(start_node.get_distance_to(end_node)/Config.PILOT_EXPECTED_VELOCITY)
    
    def check_conflict(self, requests):
        """
            Checks for conflicts in the given schedule
            Return: 
                - None if no conflict detected
                - (target_node_1, target_node_2, aircraft_1, aircraft_2) involved in the conflict
        """
        
        
        occupany_map = {}

        for request in requests:
            aircraft = request.aircraft
            itinerary = request.itinerary

            for target_node in itinerary.target_nodes:
                node = target_node.node
                for time in range(get_seconds(target_node.expected_arrival_time), get_seconds(target_node.expected_departure_time)):
                    if time not in occupany_map:
                        occupany_map[time] = {}

                    occupied_nodes = occupany_map[time]
                    if node in occupied_nodes:
                        return (occupied_nodes[node][0], target_node, occupied_nodes[node][1], aircraft)

                    occupied_nodes[node] = target_node, aircraft
        return None

    def resolve_conflict(self, conflictInfo, requests):
        """
            Params:
                - conflictInfo: (time, node, airline1, airline2) involved in the conflict
                - requests: the schedule in which the conflict occured
            Return:
                - a new schedule after resolving the conflict specfified in conflictInfo
        """

        """
        Delay the pushback of the later flight by the time taken by the earlier flight to reach 
        the next node in its path
        """
            
        target_node1, target_node2, aircraft1, aircraft2 = conflictInfo

        delay = 0
        for idx in range(len(requests)):
            request = requests[idx]
            aircraft = request.aircraft
            itinerary = request.itinerary

            if aircraft == aircraft1:
                target_nodes = itinerary.target_nodes

                for idx2 in range(len(target_nodes)):
                    if target_nodes[idx2] == target_node1:
                        delay = target_nodes[idx2+1].expected_arrival_time - target_node1.expected_departure_time

            if aircraft == aircraft2:
                for target_node in itinerary.target_nodes:
                    target_node.expected_departure_time = get_seconds_after(target_node.expected_departure_time, delay)
                    target_node.expected_arrival_time = get_seconds_after(delay, target_node.expected_arrival_time, delay)

                itinerary.start_time = get_seconds_after(itinerary.start_time, delay)

        return requests

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
