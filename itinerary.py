import logging
from copy import deepcopy
from utils import str2sha1, random_string


"""
Itinerary is a list of target nodes that an aircraft follows per tick.
"""
class Itinerary:

    def __init__(self, targets=[]):

        self.targets = targets
        self.backup = deepcopy(targets)
        self.index = 0  # If index == len(targets): completed

        self.hash = str2sha1("#".join(str(self.targets)))
        self.uncertainty_delayed_index = []
        self.scheduler_delayed_index = []

    def tick(self):
        if self.is_completed:
            return
        self.index += 1

    def __add_delay(self):
        if self.is_completed:
            return None
        self.targets.insert(self.index, self.targets[self.index])
        return self.targets[self.index]

    def add_uncertainty_delay(self):
        self.__update_delayed_index(self.index)
        self.uncertainty_delayed_index.append(self.index)
        return self.__add_delay()

    def add_scheduler_delay(self):
        self.__update_delayed_index(self.index)
        self.scheduler_delayed_index.append(self.index)
        return self.__add_delay()

    def __update_delayed_index(self, new_index):
        for i in range(len(self.uncertainty_delayed_index)):
            if self.uncertainty_delayed_index[i] >= new_index:
                self.uncertainty_delayed_index[i] += 1
        for i in range(len(self.scheduler_delayed_index)):
            if self.scheduler_delayed_index[i] >= new_index:
                self.scheduler_delayed_index[i] += 1

    def reset(self):
        self.index = 0

    def restore(self):
        # NOTE: This function doesn't work well on cleaning the delayed indexes
        # and we should avoid using this function.
        self.targets = deepcopy(self.backup)
        self.uncertainty_delayed_index = []
        self.scheduler_delayed_index = []

    @property
    def length(self):
        return len(self.targets)

    @property
    def is_delayed(self):
        if self.next_target is None:
            return False
        return self.index in \
                self.uncertainty_delayed_index + self.scheduler_delayed_index

    @property
    def current_target(self):
        if self.is_completed:
            return None
        return self.targets[self.index]

    @property
    def next_target(self):
        if self.index >= self.length - 1:
            return None
        return self.targets[self.index + 1]

    @property
    def is_completed(self):
        return self.index >= self.length

    def __repr__(self):
        return "<Itinerary: %d target>" % len(self.targets)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not(self == other)
