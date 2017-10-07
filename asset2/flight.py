from aircraft import Aircraft

class Flight:
    aircraft = None

class ArrivalFlight(Flight):

    def __init__(self, callsign, model, from_airport, to_gate, runway,
                 arrival_time, spot):

        self.aircraft = Aircraft(callsign, model, Aircraft.State.scheduled)
        self.from_airport = from_airport
        self.to_get = to_gate
        self.runway = runway
        self.arrival_time = arrival_time
        self.spot = spot

class DepartureFlight(Flight):

    def __init__(self, callsign, model, to_airport, from_gate, departure_time,
                 spot):
        self.aircraft = Aircraft(callsign, model, Aircraft.State.scheduled)
        self.to_airport = to_airport
        self.departure_time = departure_time
        self.spot = spot
