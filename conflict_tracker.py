from utils import str2sha1

conflicts = []
conflicts_snapshot = None

class Conflict:

    def __init__(self, aircraft_pair, location, time):
        self.aircraft_pair = aircraft_pair
        self.location = location
        self.time = time
        self.hash = str2sha1("%s#%s#%s" % (aircraft_pair[0],
                                           aircraft_pair[1], location))

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not(self == other)

def add_conflict(conflict):
    if not conflict in conflicts:
        conflicts.append(conflict)

def save_and_reset_conflicts():
    conflicts_snapshot = conflicts
    conflicts = []

def restore_conflicts():
    conflicts = conflicts_snapshot
    conflicts_snapshot = []

def conflicts_size():
    return len(conflicts)
