"""Class file for `StateLogger`."""
import os
import json
import logging
from utils import get_output_dir_name


class StateLogger:
    """`StateLogger` logs the airport states in each tick, parses them into a
    generic file format (JSON) and will be used for visualization. The logs are
    saved to file on the fly; therefore, the logs are still valid even the
    simulation are terminated early.
    """

    def __init__(self):

        self.states = []
        self.logger = logging.getLogger(__name__)

        try:
            os.remove(self.output_filename)
        except OSError:
            pass

    def log_on_tick(self, simulation):
        """Logs the simulation states on tick."""

        aircrafts = [
            self.__parse_aircraft(aircraft)
            for aircraft in simulation.airport.aircrafts
        ]

        state = {
            "time": self.__parse_time(simulation.now),
            "aircrafts": aircrafts
        }

        with open(self.output_filename, "a") as fout:
            fout.write(json.dumps(state) + "\n")

    def __parse_aircraft(self, aircraft):

        itinerary = self.__parse_itinerary(aircraft.itinerary)
        itinerary_index = aircraft.itinerary.index if itinerary else None

        uc_delayed_index = aircraft.itinerary.uncertainty_delayed_index\
            if itinerary else None
        sc_delayed_index = aircraft.itinerary.scheduler_delayed_index\
            if itinerary else None

        return {
            "callsign": aircraft.callsign,
            "state": aircraft.state.name,
            "is_delayed": aircraft.is_delayed,
            "location": aircraft.location.geo_pos,
            "itinerary": itinerary,
            "itinerary_index": itinerary_index,
            "uncertainty_delayed_index": uc_delayed_index,
            "scheduler_delayed_index": sc_delayed_index
        }

    @classmethod
    def __parse_itinerary(cls, itinerary):
        return [
            {
                "node_name": target.name,
                "node_location": target.geo_pos
            }
            for target in itinerary.targets
        ] if itinerary is not None else None

    @classmethod
    def __parse_time(cls, time):
        return "%02d:%02d:%02d" % (time.hour, time.minute, time.second)

    @property
    def output_filename(self):
        """Gets the output filename of json file storing all the states."""
        return get_output_dir_name() + "states.json"

    def __getstate__(self):
        attrs = dict(self.__dict__)
        del attrs["logger"]
        return attrs

    def __setstate__(self, attrs):
        self.__dict__.update(attrs)
