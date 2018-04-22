from utils import str2sha1


class Conflict:

    def __init__(self, locations, aircrafts):

        self.locations = locations
        self.aircrafts = aircrafts

        h = []
        for aircraft in aircrafts:
            h.append(aircraft.callsign)
        h.sort()

        self.hash = str2sha1("%s#%s" %
                             ("#".join(h), "#".join(str(self.locations))))

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not(self == other)

    def __repr__(self):
        return "<Conflict: %s %s>" % (self.locations, self.aircrafts)

    def get_less_priority_aircraft(self, scenario):
        f0, f1 = scenario.get_flight(self.aircrafts[0]), \
                scenario.get_flight(self.aircrafts[1])
        return (
            self.aircrafts[1]
            if f0.departure_time < f1.departure_time
            else self.aircrafts[0]
        )
