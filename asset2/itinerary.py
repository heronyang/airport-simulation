import logging
from utils import get_seconds_after

class Itinerary:

    def __init__(self, route, expected_start_time):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        if not route.is_completed:
            raise Exception("Incompleted route can't be used by an itinerary")

        self.route = route
        self.expected_start_time = expected_start_time
        self.current_location = route.start

        self.current_link_index = 0 # which link that current location lacates
        self.current_link_distance = 0 # how long had moved from the link start

    @property
    def distance_left(self):
        d = 0.0
        d += self.route.links[self.current_link_index].length - \
                self.current_link_distance
        for i in range(self.current_link_index + 1, len(self.route.links)):
            link = self.route.links[i]
            d += link.length
        return d

    @property
    def estimated_finish_time(self, velocity):
        time_needed = self.distance_left / velocity
        return get_seconds_after(Clock.now(), time_needed)

    def get_next_location(self, distance):
        # Only returns the location of the next state
        return self.get_next_state(distance)[0]

    def get_next_state(self, distance):

        if self.distance_left <= distance:
            last_index = len(self.route.links) - 1
            return (self.route.end, last_index, 
                    self.route.links[last_index].length)

        # Gets all links in route
        links = self.route.links

        # Gets current link index and distance left on that link
        link_index = self.current_link_index
        link_distance = self.current_link_distance

        while True:
            if link_distance >= distance:
                return (links[link_index].get_node_from_start(distance),
                        link_index, link_distance)
            distance -= link_distance
            link_index += 1
            link_distance = links[link_index].length

        raise Exception("Failed to get next location of this itinerary")

    def update(self, distance):
        self.current_location, self.current_link_index, 
        self.current_link_distance = self.get_next_state(distance)

    def is_completed(self):
        return self.current_location.is_close_to(self.route.end)

    def __repr__(self):
        return "<Itinerary %s to %s>" %  (self.route.start, self.route.end)
