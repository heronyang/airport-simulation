import enum

class Aircraft:

    """
    Aircraft contains information of a aircraft and states that the pilot
    knows. It won't obtain information other than its own state and operation.
    """

    class State(enum.Enum):
        unknown = 0
        scheduled = 1
        arriving = 2
        parked = 3
        departing = 4

    def __init__(self, callsign, model, state):
        self.callsign = callsign
        self.model = model
        self.state = state
