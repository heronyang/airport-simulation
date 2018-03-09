import logging
from utils import get_time_delta
from node import get_middle_node


class Itinerary:

    class TargetNode:

        """
        eat = expected arrival time
        edt = expected departure time
        """
        def __init__(self, node, eat, edt):
            self.node = node
            self.eat = eat
            self.edt = edt

        def __repr__(self):
            return "<TargetNode %s | eat %s | edt %s>" \
                    % (self.node, self.eat, self.edt)

    def __init__(self, target_nodes):

        # Setups the logger
        self.logger = logging.getLogger(__name__)
        self.target_nodes = target_nodes
        self.past_node = None

    def pop_node(self):

        # Gets the next node
        next_node = self.next_node

        # Remove the next node from the queue
        self.target_nodes = self.target_nodes[1:]

        # Saves the original next node as past node
        self.past_node = next_node

        return next_node

    def get_true_location(self, now):

        if self.past_node is None:
            # If we have't started the itinerary, use next_node
            if self.next_node:
                return self.next_node.node
            # If there's no node informations, raise exception
            raise Exception("Unable to find true location")

        total_time = get_time_delta(self.next_node.eat, self.past_node.edt)
        past_time = get_time_delta(now, self.past_node.edt)

        ratio = past_time / total_time
        return get_middle_node(self.past_node.node, self.next_node.node, ratio)

    @property
    def next_node(self):
        if len(self.target_nodes) < 1:
            raise Exception("Can't peek node while there's no target node")
        return self.target_nodes[0]

    @property
    def is_completed(self):
        return len(self.target_nodes) == 0

    def is_valid(self, now):
        # TODO: More validation can be added to avoid hidden bug
        if not self.target_nodes or len(self.target_nodes) <= 1:
            return False
        return self.target_nodes[0].edt >= now

    def __repr__(self):
        return "<Itinerary: %d target nodes>" % len(self.target_nodes)
