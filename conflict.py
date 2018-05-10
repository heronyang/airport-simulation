"""Class file for `Conflict`."""
from utils import str2sha1


class Conflict:
    """`Conflict` represents two aircrafts are too close to each other in an
    airport.
    """

    def __init__(self, locations, aircrafts):

        self.locations = locations
        self.aircrafts = aircrafts

        callsigns = []
        for aircraft in aircrafts:
            callsigns.append(aircraft.callsign)
        callsigns.sort()

        self.hash = str2sha1("%s#%s" %
                             ("#".join(callsigns),
                              "#".join(str(self.locations))))

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "<Conflict: %s %s>" % (self.locations, self.aircrafts)

    def get_less_priority_aircraft(self, scenario):
        """Retrieves the less priority aircraft between the two conflicted
        aircrafts.
        """
        first, second = (scenario.get_flight(self.aircrafts[0]),
                         scenario.get_flight(self.aircrafts[1]))
        return (
            self.aircrafts[1]
            if first.departure_time < second.departure_time
            else self.aircrafts[0]
        )
