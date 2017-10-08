class MovableNode:

    class State(enum.Enum):
        init = 0
        moving = 1
        stopped = 2
        gone = 3

    def __init__(self, state, current_position, speed, clock):
        self.state = state
        self.current_position = current_pos
        self.target_positions = []
        self.speed = speed
        self.last_move = clock.now();

    def tick(self):
        """
        Move `current_position` to 1 unit time later.
        """
        pass

    def tickTo(self, time):
        """
        Move `current_position` to a specific time
        """
        pass

    def addTarget(self, target):
        # FIXME: check if the new target is valid
        self.target_positions.append(target)
