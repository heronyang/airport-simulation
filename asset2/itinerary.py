import logging

from clock import Clock

class Itinerary:

    """
    Itinerary contains one start time, which the pilot should only operate the
    aircraft after the start time, and a list of target nodes. Each target node
    contains the expected arrival time and the expected departure time for
    moving to the target node.
    """

    class TargetNode:
        def __init__(self, node,
                     expected_arrival_time, expected_departure_time):
            self.node = node
            self.expected_arrival_time = expected_arrival_time
            self.expected_departure_time = expected_departure_time

        def __repr__(self):
            return "<TargetNode %s | exp arrive at %s | exp leave at %s>" \
                    % (self.node, self.expected_arrival_time,
                       self.expected_departure_time)

    def __init__(self, target_nodes, start_time):

        # Setups the logger
        self.logger = logging.getLogger(__name__)
        self.target_nodes = target_nodes
        self.start_time = start_time

    def pop_target_node(self):

        # Gets the next node
        next_node = self.peek_target_node()

        # Sets the start time to the expected departure time of this node
        self.start_time = next_node.expected_departure_time

        # Remove the next node from the queue
        self.target_nodes = self.target_nodes[1:]

        return next_node

    def peek_target_node(self):
        if len(self.target_nodes) < 1:
            raise Exception("Can't peek node while there's no target node")
        return self.target_nodes[0]

    @property
    def is_started(self):
        if self.is_completed:
            return False;
        return Clock.now > self.start_time

    @property
    def is_completed(self):
        return len(self.target_nodes) == 0

    def __repr__(self):
        return "<Itinerary: %d target nodes, start time %s>" % \
                (len(self.target_nodes), self.start_time)
