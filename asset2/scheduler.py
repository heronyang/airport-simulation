class FCFSScheduler:

    """ 
    Implementation of a schedule that handles airline requests on a 
    FCFS basis, depending on the earliest push-back times    
    """

    def __init__(self, requests, checker, method, debug):

        """
            Requests: List of airline requests, each request in the form (airline_id, gate, earliest_pushback_time)
            Checker: Decides which module is responsible for checking for conflicts, values in {'simulator', 'scheduler'} 
            Method: Method of resolving conflicts. Possible values are:
                    - delay_pushback: The pushback time of the later flight is delayed
            Debug: Runs scheduler in debug mode, with print messages
        """

        self.requests = sorted(requests, key = lambda x: x[2])
        self.checker = checker
        self.method = method
        self.debug = debug

    def print(self, *args):
        if self.debug:
            print(args)

    def generate_schedule(self):

        """
            Method responsible for generating the schedule based on the requests obtained
            Return: 
                -schedule: List of airline schedules, each element of the form (airline_id, [list of (node, time) tuples])
        """

        schedule = []
        for airline, gate, pushback_time in self.requests:
            route = self.getRoute(gate)
            timedRoute = []
            prev_node = None

            for node in route:
                if prev_node is None:
                    time = pushback_time
                else:
                    time += self.getDelay(prev_node, node, airline)

                timedRoute.append((node, time))
                prev_node = node


            schedule.append((airline, timedRoute))


        conflictInfo = self.checkConflict(schedule)

        # Repeatedly check for conflicts and resolve it until conflict-free schedule is obtained
        count = 0
        while conflictInfo is not None: 
            schedule = self.resolveConflict(conflictInfo, schedule)
            conflictInfo = self.checkConflict(schedule)
            count+=1
        
        for sch in schedule:
            self.print(sch)

        return schedule            
        

    def get_delay(self, start_node, end_node, airline):
        """
         Return:
            -time required for the airpline to move from start node to destination node
        """

        return 1

    def get_route(self, gate):
        """
            Return:
                -List of nodes on the route from the gate to the nearest runway
        """

        pass

    def check_conflict(self, schedule):
        """
            Checks for conflicts in the given schedule
            Return: 
                - None if no conflict detected
                - (time, node, airline1, airline2) involved in the conflict
        """
        
        # If the checker paramter is self, the scheduler itself checks for conflicts in the route
        if self.checker == 'self':
        
        # Maintain an 
            occupany_map = {}

            for airline, timedRoute in schedule:
                for node, time in timedRoute:
                    if time not in occupany_map:
                        occupany_map[time] = {}

                    occupied_nodes = occupany_map[time]
                    if node in occupied_nodes:
                        return (time, node, occupied_nodes[node], airline)

                    occupied_nodes[node] = airline
        return None

    def resolve_conflict(self, conflictInfo, schedule):
        """
            Params:
                - conflictInfo: (time, node, airline1, airline2) involved in the conflict
                - schedule: the schedule in which the conflict occured

            Return:
                - a new schedule after resolving the conflict specfified in conflictInfo
        """

        self.print("CONFLICT------------------->",conflictInfo)
        if self.method == 'delay_pushback':
            """
            Delay the pushback of the later flight by the time taken by the earlier flight to reach 
            the next node in its path
            """
            
            conf_time, conf_node, airline1, airline2 = conflictInfo

            delay = 0
            for idx in range(len(schedule)):
                airline, timedRoute = schedule[idx]
                if airline == airline1:
                    for idx2 in range(len(timedRoute)):
                        if timedRoute[idx2] == (conf_node, conf_time):
                            delay = timedRoute[idx2+1][1] - conf_time

                if airline == airline2:
                    schedule[idx] = airline, [(node, time + delay) for node, time in timedRoute]

            return schedule

class SchedulerFactory:

    @classmethod
    def create(self, requests, scheduler_type='FCFS', checker = 'self', 
        method = 'delay_pushback', debug = False):

        if scheduler_type == 'FCFS':
            return FCFSScheduler(requests, checker, method, debug)
        else:
            return None
