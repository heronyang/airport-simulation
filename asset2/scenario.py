import os
import json
import logging

from utils import str2time
from flight import ArrivalFlight, DepartureFlight
from config import Config

class Scenario:
    """
    Scenario contains a list of arrival flights and a list of depature flights.
    The flight information is designed for read-only and shall only be updated
    when we decided to change delay some certain flights. It's like the
    scenario we see on the screens in the airports.
    """

    def __init__(self, arrivals, departures):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        self.arrivals = arrivals
        self.departures = departures
        self.build_lookup_table()

    def build_lookup_table(self):
        self.flight_table = {}
        for flight in self.arrivals + self.departures:
            self.flight_table[flight.aircraft] = flight

    def __repr__(self):
        n_flights = len(self.arrivals) + len(self.departures)
        return "<Scenario: " + str(n_flights) + " flights>"

    def get_flight(self, aircraft):
        return self.flight_table[aircraft]
    
    def print_stats(self):

        # Prints arrival flights
        self.logger.debug("Scenario: arrival flights loaded")
        for flight in self.arrivals:
            self.logger.debug(flight)

        # Prints departure flights
        self.logger.debug("Scenario: departure flights loaded")
        for flight in self.departures:
            self.logger.debug(flight)

class ScenarioFactory:

    @classmethod
    def create(self, code, surface):

        # Loads file if it exists; otherwise, raises error
        dir_path = Config.DATA_ROOT_DIR_PATH % code
        file_path = dir_path+ "scenario.json"
        if not os.path.exists(file_path):
            raise Exception("Scenario file not found")
        with open(dir_path + "scenario.json") as f:
            scenario_raw = json.load(f)

        # Parse arrival flights into the array
        arrivals = []
        for af in scenario_raw["arrivals"]:
            arrivals.append(ArrivalFlight(
                af["callsign"],
                af["model"],
                af["airport"],
                surface.get_node(af["gate"]),
                surface.get_node(af["spot"]),
                surface.get_link(af["runway"]),
                str2time(af["time"]),
                str2time(af["appear_time"])
            ))

        # Parse departure flights into the array
        departures = []
        for df in scenario_raw["departures"]:
            departures.append(DepartureFlight(
                df["callsign"],
                df["model"],
                df["airport"],
                surface.get_node(df["gate"]),
                surface.get_node(df["spot"]),
                surface.get_link(df["runway"]),
                str2time(df["time"]),
                str2time(df["appear_time"])
            ))

        return Scenario(arrivals, departures)
