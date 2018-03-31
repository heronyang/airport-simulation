import logging
from utils import get_time_delta, get_seconds_after, get_seconds_before, str2sha1
from node import get_middle_node


class Itinerary:

    class Target:

        """
        eat = expected arrival time
        edt = expected departure time
        """
        def __init__(self, node, eat, edt):
            self.node = node
            self.eat = eat
            self.edt = edt
            self.hash = str2sha1("%s#%s#%s" % (self.node, self.eat, self.edt))

        def __repr__(self):
            return "<Target %s | eat %s | edt %s>" \
                    % (self.node, self.eat, self.edt)

        def __hash__(self):
            return self.hash

        def __eq__(self, other):
            return self.hash == other.hash

        def __ne__(self, other):
            return not(self == other)

    def __init__(self, targets):

        self.targets = targets
        self.past_target = None

        self.hash = str2sha1("#".join(str(self.targets)))

    def pop_target(self):

        # Gets the next node
        next_target = self.next_target

        # Remove the next node from the queue
        self.targets = self.targets[1:]

        # Saves the original next node as past node
        self.past_target = next_target

        return next_target

    def get_true_location(self, now):

        if self.past_target is None:
            # If we have't started the itinerary, use next_target
            if self.next_target:
                return self.next_target.node
            # If there's no node informations, raise exception
            raise Exception("Unable to find true location")

        total_time = get_time_delta(self.next_target.eat, self.past_target.edt)
        past_time = get_time_delta(now, self.past_target.edt)

        ratio = past_time / total_time
        return get_middle_node(self.past_target.node,
                               self.next_target.node, ratio)

    def add_delay(self, delay):
        is_first = True
        for target in self.targets:
            if target.edt is None:
                break
            target.edt = get_seconds_after(target.edt, delay)
            if not is_first:
                # the expected arrival time of the next node is fixed
                target.eat = get_seconds_after(target.eat, delay)
            is_first = False

    def remove_delay(self, delay):
        is_first = True
        for target in self.targets:
            if target.edt is None:
                break
            target.edt = get_seconds_before(target.edt, delay)
            if not is_first:
                # the expected arrival time of the next node is fixed
                target.eat = get_seconds_before(target.eat, delay)
            is_first = False

    @property
    def next_target(self):
        if len(self.targets) < 1:
            raise Exception("Can't peek node while there's no target node")
        return self.targets[0]

    @property
    def is_completed(self):
        return len(self.targets) == 0

    def is_valid(self, now):
        # TODO: More validation can be added to avoid hidden bug
        if not self.targets or len(self.targets) <= 1:
            return False
        return self.targets[0].edt >= now

    def __repr__(self):
        return "<Itinerary: %d target>" % len(self.targets)

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not(self == other)
