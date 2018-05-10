"""Class file for `Scenario`."""
import os
import json
import logging

from utils import str2time
from flight import ArrivalFlight, DepartureFlight
from config import Config


class Scenario:
    """Scenario contains a list of arrival flights and a list of depature
    flights.  The flight information is designed for read-only and shall only
    be updated when we decided to change delay some certain flights. It's like
    the scenario we see on the screens in the airports.
    """

    def __init__(self, arrivals, departures):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        self.arrivals = arrivals
        self.departures = departures
        self.__build_lookup_table()

    def __build_lookup_table(self):
        self.flight_table = {}
        for flight in self.arrivals + self.departures:
            self.flight_table[flight.aircraft] = flight

    def __repr__(self):
        n_flights = len(self.arrivals) + len(self.departures)
        return "<Scenario: " + str(n_flights) + " flights>"

    def get_flight(self, aircraft):
        """Gets a flight of a given aircraft."""
        return self.flight_table[aircraft]

    def print_stats(self):
        """Prints the statistics of this scenario."""

        # Prints arrival flights
        self.logger.debug("Scenario: arrival flights loaded")
        for flight in self.arrivals:
            self.logger.debug(flight)

        # Prints departure flights
        self.logger.debug("Scenario: departure flights loaded")
        for flight in self.departures:
            self.logger.debug(flight)

    def __getstate__(self):
        atts = dict(self.__dict__)
        del atts["logger"]
        return atts

    def __setstate__(self, atts):
        self.__dict__.update(atts)

    def set_quiet(self, logger):
        """Sets this object into quiet mode where less logs are printed."""
        self.logger = logger
        for flight in self.departures:
            flight.aircraft.set_quiet(logger)

    @classmethod
    def create(cls, name, surface):
        """Generates a scenario using the gvien name of the airport and the
        surface data.
        """

        # Loads file if it exists; otherwise, raises error
        dir_path = Config.DATA_ROOT_DIR_PATH % name
        file_path = dir_path + "scenario.json"
        if not os.path.exists(file_path):
            raise Exception("Scenario file not found")
        with open(dir_path + "scenario.json") as fin:
            scenario_raw = json.load(fin)

        # Parse arrival flights into the array
        arrivals = []
        for arrival in scenario_raw["arrivals"]:
            arrivals.append(ArrivalFlight(
                arrival["callsign"],
                arrival["model"],
                arrival["airport"],
                surface.get_node(arrival["gate"]),
                surface.get_node(arrival["spot"]),
                surface.get_link(arrival["runway"]),
                str2time(arrival["time"]),
                str2time(arrival["appear_time"])
            ))

        # Parse departure flights into the array
        departures = []
        for departure in scenario_raw["departures"]:
            departures.append(DepartureFlight(
                departure["callsign"],
                departure["model"],
                departure["airport"],
                surface.get_node(departure["gate"]),
                surface.get_node(departure["spot"]),
                surface.get_link(departure["runway"]),
                str2time(departure["time"]),
                str2time(departure["appear_time"])
            ))

        return Scenario(arrivals, departures)
