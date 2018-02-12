from utils import str2sha1

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

class ConflictTracker:

    def __init__(self):
        self.conflicts = []

    def add_conflict(self, conflict):
        if not conflict in self.conflicts:
            self.conflicts.append(conflict)

    @property
    def size(self):
        return len(self.conflicts)
