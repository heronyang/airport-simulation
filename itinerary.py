import logging
from copy import deepcopy
from utils import get_time_delta, get_seconds_after, get_seconds_before, str2sha1
from node import get_middle_node


"""
Itinerary is a list of target nodes that an aircraft follows per tick.
"""
class Itinerary:

    def __init__(self, targets=[]):

        self.targets = targets
        self.past_target = None

        self.hash = str2sha1("#".join(str(self.targets)))

    def tick(self):

        if self.is_completed:
            return

        next_target = self.next_target
        self.targets = self.targets[1:]
        self.past_target = next_target

    def add_delay(self):
        if self.is_completed:
            return
        self.targets.insert(0, self.targets[0])

    @property
    def next_target(self):
        if len(self.targets) < 1:
            return None
        return self.targets[0]

    @property
    def is_completed(self):
        return len(self.targets) == 0

    def __repr__(self):
        return "<Itinerary: %d target>" % len(self.targets)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not(self == other)
