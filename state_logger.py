import json
import logging
from config import Config
from utils import get_output_dir_name

class StateLogger:

    def __init__(self):
        self.states = []
        self.logger = logging.getLogger(__name__)

    def log_on_tick(self, simulation):

        aircrafts = [
            self.parse_aircraft(aircraft)
            for aircraft in simulation.airport.aircrafts
        ]

        self.states.append({
            "time": self.parse_time(simulation.now),
            "aircrafts": aircrafts
        })

    def parse_aircraft(self, aircraft):
        itinerary = self.parse_itinerary(aircraft.itinerary)
        return {
            "callsign": aircraft.callsign,
            "state": aircraft.state.name,
            "location": aircraft.location.geo_pos,
            "itinerary": itinerary
        }

    def parse_itinerary(self, itinerary):

        return [
            {
                "node_name": target.name,
                "node_location": target.geo_pos
            }
            for target in itinerary.targets
        ] if itinerary is not None else None

    def parse_time(self, time):
        return "%02d:%02d:%02d" % (time.hour, time.minute, time.second)

    def save(self):
        filename = get_output_dir_name() + "states.json"
        with open(filename, "w") as f:
            f.write(json.dumps(self.states, indent=4))
        self.logger.info("States saved to %s" % filename)

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
