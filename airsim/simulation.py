import airport

class Simulation:

    def __init__(self, airport_code):
        self.airport_code = airport_code
        self.airport_manager = airport.Manager(airport_code)

    def update(self):
        pass

    def close(self):
        pass

    def get_airport(self):
        return self.airport_manager.airport

    def get_static_state(self):
        # TODO: incompleted
        return None

    def get_runtime_state(self):
        # TODO: incompleted
        return None
