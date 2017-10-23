from aircraft import Aircraft

class Flight:

    def __init__():
        self.aircraft = None

class ArrivalFlight(Flight):

    def __init__(self, callsign, model, from_airport, to_gate, runway, spot,
                 arrival_time):

        self.aircraft = Aircraft(callsign, model, Aircraft.State.scheduled,
                                 None)
        self.from_airport = from_airport
        self.to_get = to_gate
        self.runway = runway
        self.spot = spot
        self.arrival_time = arrival_time

    def __repr__(self):
        return "<Arrival: " + self.aircraft.callsign + ">"

class DepartureFlight(Flight):

    def __init__(self, callsign, model, to_airport, spot, runway, departure_time):
        self.aircraft = Aircraft(callsign, model, Aircraft.State.scheduled,
                                 None)
        self.to_airport = to_airport
        self.spot = spot
        self.runway = runway
        self.departure_time = departure_time

    def __repr__(self):
        return "<Departure: " + self.aircraft.callsign + ">"
