"""Class file for `Itinerary`."""
from copy import deepcopy
from utils import str2sha1


class Itinerary:
    """Itinerary is a list of target nodes that an aircraft follows per tick.
    """

    def __init__(self, targets=None):

        if targets is None:
            targets = []

        self.targets = targets
        self.backup = deepcopy(targets)
        self.index = 0

        self.hash = str2sha1("#".join(str(self.targets)))
        self.uncertainty_delayed_index = []
        self.scheduler_delayed_index = []

    def tick(self):
        """Ticks this itinerary for moving to the next state."""
        if self.is_completed:
            return
        self.index += 1

    def __add_delay(self):
        if self.is_completed:
            return None
        self.targets.insert(self.index, self.targets[self.index])
        return self.targets[self.index]

    def add_uncertainty_delay(self, amount=1):
        """Adds `amount` of uncertainty delays at the head of this itinerary.
        """
        for _ in range(amount):
            self.__update_delayed_index(self.index)
            self.uncertainty_delayed_index.append(self.index)
            self.__add_delay()

    def add_scheduler_delay(self):
        """Adds a single scheduler delay at the head of this itinerary."""
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
        """Reset the index of this itinerary."""
        self.index = 0

    @property
    def length(self):
        """Returns the length of this itinerary."""
        return len(self.targets)

    @property
    def is_delayed_by_uncertainty(self):
        """Returns true if the next tick is delayed by the uncertainty."""
        if self.next_target is None or self.index <= 0:
            return False
        return self.index - 1 in self.uncertainty_delayed_index

    @property
    def is_delayed_by_uncertainty_now(self):
        """Returns true if the current tick is delayed by the uncertainty."""
        return self.index in self.uncertainty_delayed_index

    @property
    def is_delayed_by_scheduler(self):
        """Returns true if the next tick is delayed by the scheduler."""
        if self.next_target is None or self.index <= 0:
            return False
        return self.index - 1 in self.scheduler_delayed_index

    @property
    def is_delayed(self):
        """Returns true if the next tick is delayed."""
        return self.is_delayed_by_scheduler or self.is_delayed_by_uncertainty

    @property
    def current_target(self):
        """Returns the current target."""
        if self.is_completed:
            return None
        return self.targets[self.index]

    @property
    def next_target(self):
        """Returns the next target."""
        if self.index >= self.length - 1:
            return None
        return self.targets[self.index + 1]

    @property
    def is_completed(self):
        """Returns true if this itinerary had been completed."""
        return self.index >= self.length

    @property
    def n_scheduler_delay(self):
        """Returns the number of delays added by the scheduler."""
        return len(self.scheduler_delayed_index)

    @property
    def n_uncertainty_delay(self):
        """Returns the number of delays added by the uncertainty."""
        return len(self.uncertainty_delayed_index)

    @property
    def n_future_uncertainty_delay(self):
        """Returns the number of delays added by the uncertainty from now on.
        """
        return len([i for i in self.uncertainty_delayed_index
                    if i >= self.index])

    def __repr__(self):
        return "<Itinerary: %d target>" % len(self.targets)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not self == other
