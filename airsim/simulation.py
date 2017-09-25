from surface_manager import SurfaceManager

class Simulation:

    def __init__(self, airport_code):
        self.airport_code = airport_code
        self.surface_manager = SurfaceManager(airport_code)
