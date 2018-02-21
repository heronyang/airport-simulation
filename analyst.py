import logging
import pandas as pd

from clock import Clock
from aircraft import State
from utils import get_time_delta

class TaxitimeMetric():

    def __init__(self, sim_time):

        self.moving_aircraft_count_on_tick = 0
        self.sim_time = sim_time

    def update_on_tick(self, aircrafts, scenario):

        for aircraft in aircrafts:
            # If an aircraft is not close to its gate, it's on its taxiway
            flight = scenario.get_flight(aircraft)
            if not aircraft.location.is_close_to(flight.from_gate):
                self.moving_aircraft_count_on_tick += 1

    @property
    def taxi_time(self):
        return self.moving_aircraft_count_on_tick * self.sim_time
    
    @property
    def summary(self):
        return "Taxitime: %d seconds\n" % self.taxi_time


class MakespanMetric():

    def __init__(self):

        self.aircraft_first_time = None
        self.aircraft_last_time = None

    def update_on_tick(self, aircrafts, now):

        if len(aircrafts) == 0:
            return

        if self.aircraft_first_time is not None:
            self.aircraft_first_time = now
        self.aircraft_last_time = now

    @property
    def is_ready(self):
        return self.aircraft_first_time and self.aircraft_last_time

    @property
    def makespan(self):
        return (get_time_delta(self.aircraft_last_time,
                               self.aircraft_first_time)
                if self.is_ready else 0)

    @property
    def summary(self):

        if not self.is_ready:
            return "Makespan: insufficient data"

        return "Makespan: %d seconds\n" %  self.makespan


class AircraftCountMetric():

    def __init__(self):

        self.counter = pd.DataFrame(columns=["time", "count"])

    def update_on_tick(self, aircrafts, now):

        self.counter = self.counter.append(
            {"time": now, "count": len(aircrafts)}, ignore_index=True)

    @property
    def summary(self):

        if len(self.counter) == 0:
            return "Aircraft count: insufficient data"

        cr = self.counter.set_index("time")
        return "Aircraft count: top %d low %d mean %d remaining %d" % \
                (cr.max(), cr.min(), cr.mean(), cr.iloc[-1])


class Analyst:

    def __init__(self, sim_time):

        self.logger = logging.getLogger(__name__)

        self.taxitime_metric = TaxitimeMetric(sim_time)
        self.makespan_metric = MakespanMetric()
        self.aircraft_count_metric = AircraftCountMetric()

    def observe_on_tick(self, simulation):

        aircrafts = simulation.airport.aircrafts
        scenario = simulation.scenario
        now = simulation.now

        self.taxitime_metric.update_on_tick(aircrafts, scenario)
        self.makespan_metric.update_on_tick(aircrafts, now)
        self.aircraft_count_metric.update_on_tick(aircrafts, now)

    def print_summary(self, simulation):

        self.logger.debug(self.taxitime_metric.summary)
        self.logger.debug(self.makespan_metric.summary)
        self.logger.debug(self.aircraft_count_metric.summary)

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
