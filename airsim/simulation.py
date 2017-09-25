from surface_manager import SurfaceManager

class Simulation:

    def __init__(self, airport_code):
        self.airport_code = airport_code
        self.surface_manager = SurfaceManager(airport_code)

    def get_static_state(self):
        return {
            "surface": self.surface_manager.surface
        }

    def get_runtime_state(self):
        # TODO: incompleted
        return None
