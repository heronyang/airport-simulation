import os
import json
import logging
from config import Config
from utils import get_output_dir_name

class StateLogger:

    def __init__(self):

        self.states = []
        self.logger = logging.getLogger(__name__)

        try:
            os.remove(self.output_filename)
        except OSError:
            pass

    def log_on_tick(self, simulation):

        aircrafts = [
            self.parse_aircraft(aircraft)
            for aircraft in simulation.airport.aircrafts
        ]

        state = {
            "time": self.parse_time(simulation.now),
            "aircrafts": aircrafts
        }

        with open(self.output_filename, "a") as f:
            f.write(json.dumps(state) + "\n")

    def parse_aircraft(self, aircraft):
        itinerary = self.parse_itinerary(aircraft.itinerary)
        itinerary_index = aircraft.itinerary.index if itinerary else None
        return {
            "callsign": aircraft.callsign,
            "state": aircraft.state.name,
            "is_delayed": aircraft.is_delayed,
            "location": aircraft.location.geo_pos,
            "itinerary": itinerary,
            "itinerary_index": itinerary_index
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
        self.logger.info("States had been saved to %s" % self.output_filename)

    @property
    def output_filename(self):
        return get_output_dir_name() + "states.json"

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
