# TODO
class Itinerary:

    def __init__(self, route, expected_start_time):
        self.route = route
        self.expected_start_time = expected_start_time
        self.current_location = route.start

    @property
    def distance_left(self):
        return 0

    @property
    def estimated_finish_time(self, v):
        return 0

    def get_next_location(self, distance):
        # self.current_location += distance
        return self.current_location

    def update(self, distance):
        pass

    def is_completed(self):
        return self.current_location.is_close_to(self.route.end)
