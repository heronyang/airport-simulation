"""`Flight` is extended by `ArrivalFlight` and `DepartureFlight` to cover all
possible flight that is planned before the simulation started.
"""
from aircraft import Aircraft, State


class Flight:
    """`Flight` is the parent class for the `ArrivalFlight` and
    `DepartureFlight`.
    """

    def __init__(self, aircraft):
        self.aircraft = aircraft


class ArrivalFlight(Flight):
    """`ArrivalFlight` represents an arrival flight where its expected arrival
    time, runway, spot position, and gate are assigned.
    """

    def __init__(self, callsign, model, from_airport, to_gate,
                 spot, runway, arrival_time, appear_time):

        super().__init__(Aircraft(callsign, model, None, State.flying))
        self.from_airport = from_airport
        self.to_gate = to_gate
        self.spot = spot
        self.runway = runway
        self.arrival_time = arrival_time
        self.appear_time = appear_time

    def __repr__(self):
        return "<Arrival:%s time:%s appear:%s>" \
                % (self.aircraft.callsign, self.arrival_time, self.appear_time)


class DepartureFlight(Flight):
    """`DepartureFlight` represents a depature flight where its expected
    departure time, gate, spot position, and runway are assigned.
    """

    def __init__(self, callsign, model, to_airport, from_gate,
                 spot, runway, departure_time, appear_time):
        super().__init__(Aircraft(callsign, model, None, State.stop))
        self.to_airport = to_airport
        self.from_gate = from_gate
        self.spot = spot
        self.runway = runway
        self.departure_time = departure_time
        self.appear_time = appear_time

    def __repr__(self):
        return "<Departure:%s time:%s appear:%s>" % \
                (self.aircraft.callsign, self.departure_time, self.appear_time)
