from utils import str2sha1

class Conflict:

    def __init__(self, location, aircrafts, time):

        self.location = location
        self.aircrafts = aircrafts
        self.time = time

        h = []
        for aircraft in aircrafts:
            h.append(aircraft.callsign)
        h.sort()

        self.hash = str2sha1("%s#%s" % ("#".join(h), location))

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not(self == other)

    def __repr__(self):
        return "<Conflict: %s %s>" % (self.location, self.aircrafts)

class ConflictTracker:

    def __init__(self, simulation):
        self.simulation = simulation
        self.conflicts = []

    def add_conflict(self, conflict):
        if not conflict in self.conflicts:
            self.conflicts.append(conflict)

    def add_conflicts(self, conflicts):
        for conflict in conflicts:
            self.add_conflict(conflict)

    def count(self):
        return len(self.conflicts)

    def tick(self):
        self.add_conflict(self.simulation.airport.conflicts)

    @property
    def size(self):
        return len(self.conflicts)
