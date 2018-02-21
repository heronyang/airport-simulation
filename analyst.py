import logging
import pandas as pd

from clock import Clock
from aircraft import State
from utils import get_time_delta
from config import Config


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
        return "Taxitime: %d seconds" % self.taxi_time


class MakespanMetric():

    def __init__(self):

        self.aircraft_first_time = None
        self.aircraft_last_time = None

    def update_on_tick(self, aircrafts, now):

        if len(aircrafts) == 0:
            return

        if self.aircraft_first_time is None:
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

        return "Makespan: %d seconds" % self.makespan


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

        c = self.counter.set_index("time")
        return ("Aircraft count: top %d low %d mean %d remaining %d" %
                (c.max(), c.min(), c.mean(), c.iloc[-1]))


class ConflictMetric():

    def __init__(self):

        self.conflict_nodes = pd.DataFrame(columns=["time", "count"])
        self.conflict_aircrafts = pd.DataFrame(columns=["time", "count"])

    def update_on_tick(self, conflicts, now):

        self.conflict_nodes = self.conflict_nodes.append(
            {"time": now, "count": len(conflicts)}, ignore_index=True
        )

        n_aircrafts = 0
        for c in conflicts:
            n_aircrafts += len(c.aircrafts)

        self.conflict_aircrafts = self.conflict_aircrafts.append(
            {"time": now, "count": n_aircrafts}, ignore_index=True
        )

        if len(conflicts) is not 0:
            print(conflicts)
            # from IPython.core.debugger import Tracer; Tracer()()

    @property
    def summary(self):

        if len(self.conflict_nodes) == 0 or len(self.conflict_aircrafts) == 0:
            return "Conflict: insufficient data"

        cn = self.conflict_nodes.set_index("time")
        ca = self.conflict_aircrafts.set_index("time")
        return (
            "Conflict nodes: top %d low %d mean %d, "
            "aircrafts: top %d low %d mean %d" %
            (
                cn.max(), cn.min(), cn.mean(),
                ca.max(), ca.min(), ca.mean()
            )
        )


class Analyst:

    def __init__(self, sim_time):

        self.logger = logging.getLogger(__name__)

        self.taxitime_metric = TaxitimeMetric(sim_time)
        self.makespan_metric = MakespanMetric()
        self.aircraft_count_metric = AircraftCountMetric()
        self.conflict_metric = ConflictMetric()

    def observe_on_tick(self, simulation):

        now = simulation.now
        aircrafts = simulation.airport.aircrafts
        scenario = simulation.scenario
        conflicts = simulation.airport.conflicts

        self.taxitime_metric.update_on_tick(aircrafts, scenario)
        self.makespan_metric.update_on_tick(aircrafts, now)
        self.aircraft_count_metric.update_on_tick(aircrafts, now)
        self.conflict_metric.update_on_tick(conflicts, now)

    def print_summary(self, simulation):

        self.logger.debug(self.taxitime_metric.summary)
        self.logger.debug(self.makespan_metric.summary)
        self.logger.debug(self.aircraft_count_metric.summary)
        self.logger.debug(self.conflict_metric.summary)

        if Config.params["analyst"]["details"]:

            c = self.aircraft_count_metric.counter.set_index("time")
            cr = self.conflict_metric.conflict_nodes.set_index("time")
            ca = self.conflict_metric.conflict_aircrafts.set_index("time")

            stats = c.join(
                cr, lsuffix='_aircraft',
                rsuffix="_conflict_nodes"
            ).join(
                ca,
                rsuffix="_conflict_aircrafts"
            )

            with pd.option_context("display.max_rows", None):
                self.logger.debug("\n" + str(stats))

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
