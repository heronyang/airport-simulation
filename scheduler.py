import logging

from schedule import Schedule
from aircraft import Aircraft, State
from route import Route
from itinerary import Itinerary
from config import Config
from utils import get_seconds_after, get_seconds
import math

class Scheduler:

    def __init__(self):

        # Setups the logger
        self.logger = logging.getLogger(__name__)
        self.last_occupied_time = {}

    def schedule(self, simulation, time, tightness, uc_range):

        # simulation.airport : all airport states
        # simulation.routing_expert : gets routes from node A to node B
        # time : current simulated time of a day
        self.logger.debug("Scheduling starts")
        self.logger.debug("Found %d aircrafts %s",
                          len(simulation.airport.aircrafts), simulation.airport.aircrafts)

        # helper function:
        # conflicts = simulation.predict_state_after(schedule, time_from_now)

        # put break point:
        # from IPython.core.debugger import Tracer; Tracer()()
        
        requests = []
        nodes_tightness = {}
        schedule_limit = get_seconds_after(time, simulation.reschedule_time)
        delayed_aircrafts = []
        
        for aircraft in simulation.airport.aircrafts:

            # Pulls outs the flight information
            flight = simulation.scenario.get_flight(aircraft)

            if aircraft.is_idle  or aircraft.pilot.state == State.moving:

                # Gets the route from the routing expert
                # NOTE: We use runway start node as the destination of a
                # departure flight


               if aircraft.location.is_close_to(flight.from_gate):

               	if aircraft.pilot.state == State.moving:
               		from_location = flight.from_gate 
               	else:
               		from_location = aircraft.location
                
                route = simulation.routing_expert.get_shortest_route(
                    from_location, flight.runway.start)
                self.logger.debug("Get route: %s" % route)

                # Generates the itinerary for this aircraft
                target_nodes = []
                prev_node = None
                start_time = flight.departure_time
                is_delayed = False

                for node in route.nodes:

                    prev_time = 0 if node not in self.last_occupied_time else get_seconds(self.last_occupied_time[node])

                    if prev_node is None:
                        if node in self.last_occupied_time:
                            tightness_time = get_seconds_after(self.last_occupied_time[node], tightness)
                            
                            if tightness_time > schedule_limit:
                               delayed_aircrafts.append((aircraft, tightness_time))
                               is_delayed = True
                               break

                            arr_time = max(flight.departure_time, tightness_time)
                            start_time = arr_time
                        else:   
                            arr_time = flight.departure_time
    
                    else:
                        if node in self.last_occupied_time:
                            moving_time = get_seconds_after(arr_time, self.get_delay(prev_node, node))
                            tightness_time = get_seconds_after(self.last_occupied_time[node], tightness) 
                            arr_time = max(moving_time, tightness_time)
                            self.logger.debug("Taking max of move time %s and tightness_time %s \
                                (using last_occupied_time %s) which is %s", moving_time, tightness_time, self.last_occupied_time[node], arr_time)
                        else: 	                 	
                            arr_time = get_seconds_after(arr_time, self.get_delay(prev_node, node))

                    dep_time = arr_time

                    self.last_occupied_time[node] = dep_time
                    self.logger.debug("Last occupied time for %s updated to %s", node, dep_time)
                    time_diff = get_seconds(arr_time) - prev_time

                    if prev_time>0:
	                    nodes_tightness[node] = time_diff if node not in nodes_tightness \
    	                	else min(time_diff, nodes_tightness[node])

                    self.logger.debug("Target node is : %s, %s", node, arr_time)
                    target_nodes.append(
                        Itinerary.TargetNode(node, arr_time, dep_time))
                    
                    prev_node = node
                
                if is_delayed:
                    continue

                itinerary = Itinerary(target_nodes, start_time)
                self.logger.debug("Itinerary generated: %s for aircraft %s with departure_time %s", itinerary, aircraft, flight.departure_time)
                requests.append(Schedule.Request(aircraft, itinerary))
                self.logger.debug("Adds route %s on %s" % (route, aircraft))

        tightness_vals = nodes_tightness.values()
        if len(tightness_vals)>0:
	        actual_tightness = sum(tightness_vals)/float(len(tightness_vals))
        else:
            actual_tightness = tightness
        conflictInfo = self.check_conflict(requests)

        # Repeatedly check for conflicts and resolve it until conflict-free schedule is obtained
        count = 0
        while conflictInfo is not None: 
            self.logger.debug("Conflict detected at : %s", conflictInfo)
            requests = self.resolve_conflict(conflictInfo, requests)
            conflictInfo = self.check_conflict(requests)
            count+=1
        
        self.logger.debug("Scheduling done with tightness: %f", actual_tightness)
        return Schedule(requests, delayed_aircrafts, actual_tightness)

    def get_delay(self, start_node, end_node):
        """
         Return:
            -time required for the airpline to move from start node to destination node
        """

        return int(math.ceil(start_node.get_distance_to(end_node)/Config.PILOT_EXPECTED_VELOCITY))
    
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
                for time in range(get_seconds(target_node.expected_arrival_time)-60, get_seconds(target_node.expected_departure_time)+60):
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
                        if idx2+1 < len(target_nodes):
                            delay = get_seconds(target_nodes[idx2+1].expected_arrival_time) - get_seconds(target_node1.expected_departure_time)
                        else:
                            delay = get_seconds(target_node1.expected_arrival_time) - get_seconds(target_nodes[idx2-1].expected_departure_time)

            if aircraft == aircraft2:

                self.logger.debug("old itinerary %s for aircraft %s; adding delay %d ", requests[idx].itinerary, requests[idx].aircraft, delay)
                for target_node in itinerary.target_nodes:
                    target_node.expected_departure_time = get_seconds_after(target_node.expected_departure_time, delay)
                    target_node.expected_arrival_time = get_seconds_after(target_node.expected_arrival_time, delay)

                itinerary.start_time = get_seconds_after(itinerary.start_time, delay)

                requests[idx].itinerary = itinerary

                self.logger.debug("new itinerary %s for aircraft %s ", requests[idx].itinerary, requests[idx].aircraft)
        
        return requests

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)