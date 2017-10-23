import os
import json

from utils import str2time
from flight import ArrivalFlight, DepartureFlight

class Schedule:
    """
    Schedule contains a list of arrival flights and a list of depature flights.
    The flight information is designed for read-only and shall only be updated
    when we decided to change delay some certain flights. It's like the
    schedule we see on the screens in the airports.
    """

    def __init__(self, arrivals, departures):
        self.arrivals = arrivals
        self.departures = departures

    def delay(self, flight, time_length):
        # TODO: pull out the flight from the array and update its ETA/ETD
        pass

    def __repr__(self):
        n_flights = len(self.arrivals) + len(self.departures)
        return "<Schedule: " + str(n_flights) + " flights>"

class ScheduleFactory:

    @classmethod
    def create(self, dir_path, surface):

        # Loads file if it exists; otherwise, raises error
        file_path = dir_path+ "schedule.json"
        if not os.path.exists(file_path):
            raise Exception("Schedule file not found")
        with open(dir_path + "schedule.json") as f:
            schedule_raw = json.load(f)

        # Parse arrival flights into the array
        arrivals = []
        for af in schedule_raw["arrivals"]:
            arrivals.append(ArrivalFlight(
                af["callsign"], af["model"], af["airport"],
                surface.get_node(af["gate"]), surface.get_link(af["runway"]),
                str2time(af["time"]), surface.get_node(af["spot"])
            ))

        # Parse departure flights into the array
        departures = []
        for df in schedule_raw["departures"]:
            departures.append(DepartureFlight(
                df["callsign"], df["model"], df["airport"],
                surface.get_node(df["spot"]), surface.get_link(df["runway"]),
                str2time(df["time"])
            ))

        return Schedule(arrivals, departures)
