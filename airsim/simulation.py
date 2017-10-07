import airport

from airport import AirportFactory

class Simulation:

    def __init__(self, airport_code):
        self.airport = AirportFactory.create(airport_code)

    def update(self):
        pass

    def close(self):
        pass

    def get_static_state(self):
        # TODO: incompleted
        return None

    def get_runtime_state(self):
        # TODO: incompleted
        return None
