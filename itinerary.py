import logging

from clock import Clock

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

    def pop_node(self):

        # Gets the next node
        next_node = self.next_node

        # Remove the next node from the queue
        self.target_nodes = self.target_nodes[1:]
        return next_node

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
