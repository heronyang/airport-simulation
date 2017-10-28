# TODO
class Itinerary:

    def __init__(self, route, expected_start_time):
        self.route = route
        self.expected_start_time = expected_start_time

    @property
    def distance_left(self):
        return 0

    def get_estimated_finish_time(self, v):
        return 0

    def move_distance_feet(self, distance):
        # self.current_location += distance
        return self.current_location

    def is_completed(self):
        return self.current_location.is_close_to(self.route.end)
