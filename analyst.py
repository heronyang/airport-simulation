import logging
import pandas as pd
import json
import os

from clock import Clock
from aircraft import State
from utils import get_time_delta, get_output_dir_name
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

        self.conflict_node = pd.DataFrame(columns=["time", "count"])
        self.conflict_node_aircraft = \
                pd.DataFrame(columns=["time", "count"])
        self.conflict = pd.DataFrame(columns=["time", "count"])

    def update_on_tick(self, conflicts_at_node, conflicts, now):

        self.conflict_node = self.conflict_node.append(
            {"time": now, "count": len(conflicts_at_node)}, ignore_index=True
        )

        n_aircrafts = 0
        for c in conflicts_at_node:
            n_aircrafts += len(c.aircrafts)

        self.conflict_node_aircraft = \
                self.conflict_node_aircraft.append(
                    {"time": now, "count": n_aircrafts}, ignore_index=True
                )

        self.conflict = self.conflict.append(
            {"time": now, "count": len(conflicts)}, ignore_index=True
        )

    @property
    def total_conflicts(self):
        return self.conflict["count"].sum()

    @property
    def summary(self):

        if len(self.conflict_node) == 0 or \
           len(self.conflict_node_aircraft) == 0:
            return "Conflict: insufficient data"

        cn = self.conflict_node.set_index("time")
        ca = self.conflict_node_aircraft.set_index("time")
        cf = self.conflict.set_index("time")
        return (
            "Conflict nodes: top %d low %d mean %d, "
            "aircrafts: top %d low %d mean %d, " 
            "all: top %d low %d mean %d" %
            (
                cn.max(), cn.min(), cn.mean(),
                ca.max(), ca.min(), ca.mean(),
                cf.max(), cf.min(), cf.mean()
            )
        )

class GateQueueMetric():

    def __init__(self, surface):
        self.gate_queue_size = pd.DataFrame(columns=["time", "size"])
        self.n_gates = len(surface.gates)

    def update_on_tick(self, airport, now):

        s = 0
        for _, queue in airport.gate_queue.items():
            s += len(queue)

        avg_queue_size = s / self.n_gates
        self.gate_queue_size = self.gate_queue_size.append(
            {"time": now, "size": avg_queue_size}, ignore_index=True
        )

    @property
    def avg_queue_size(self):
        return self.gate_queue_size["size"].mean()

    @property
    def summary(self):

        if len(self.gate_queue_size) == 0:
            return "Gate Queue: insufficient data"

        qs = self.gate_queue_size.set_index("time")

        return "Gate Queue: top %d low %d mean %d" % (
            qs.max(), qs.min(), qs.mean()
        )

class ScheduleMetric():

    def __init__(self):

        self.delay_added = pd.DataFrame(columns=["time", "n_delay_added"])

    def update_on_reschedule(self, schedule, now):

        self.delay_added = self.delay_added.append(
            {"time": now, "n_delay_added": schedule.n_delay_added},
            ignore_index= True
        )

    @property
    def total_delay_time_added(self):
        delay_time = Config.params["scheduler"]["delay_time"]
        return self.delay_added["n_delay_added"].sum() * delay_time

    @property
    def summary(self):

        if len(self.delay_added) == 0:
            return "Schedule: insufficient data"

        nd = self.delay_added.set_index("time")

        return "Schedule # delayed added: top %d low %d mean %d" % (
            nd.max(), nd.min(), nd.mean()
        )

class ExecutionTimeMetric():

    def __init__(self):
        # Reschedule execution time
        self.rs_exec_time = pd.DataFrame(
            columns=["time", "rs_exec_time"])

    def update_on_reschedule(self, rs_exec_time, now):
        self.rs_exec_time = self.rs_exec_time.append(
            {"time": now, "rs_exec_time": rs_exec_time},
            ignore_index = True)

    @property
    def avg_reschedule_exec_time(self):
        return self.rs_exec_time["rs_exec_time"].mean()

    @property
    def summary(self):
        
        if len(self.rs_exec_time) == 0:
            return "Execution Time: insufficient data"

        rst = self.rs_exec_time.set_index("time")

        return "Reschedule execution time: top %d low %d mean %d" % (
            rst.max(), rst.min(), rst.mean()
        )

class Analyst:

    def __init__(self, simulation):

        self.logger = logging.getLogger(__name__)

        sim_time = simulation.clock.sim_time

        self.taxitime_metric = TaxitimeMetric(sim_time)
        self.makespan_metric = MakespanMetric()
        self.aircraft_count_metric = AircraftCountMetric()
        self.conflict_metric = ConflictMetric()
        self.gate_queue_metric = GateQueueMetric(simulation.airport.surface)
        self.schedule_metric = ScheduleMetric()
        self.execution_time_metric = ExecutionTimeMetric()

    def observe_on_tick(self, simulation):

        now = simulation.now
        airport = simulation.airport
        aircrafts = airport.aircrafts
        scenario = simulation.scenario
        conflicts_at_node = simulation.airport.conflicts_at_node
        conflicts = simulation.airport.conflicts

        self.taxitime_metric.update_on_tick(aircrafts, scenario)
        self.makespan_metric.update_on_tick(aircrafts, now)
        self.aircraft_count_metric.update_on_tick(aircrafts, now)
        self.conflict_metric.update_on_tick(conflicts_at_node, conflicts, now)
        self.gate_queue_metric.update_on_tick(airport, now)

    def observe_on_reschedule(self, schedule, simulation):
        now = simulation.now
        self.schedule_metric.update_on_reschedule(schedule, now)
        self.execution_time_metric.update_on_reschedule(
            simulation.last_schedule_exec_time, now)

    def print_summary(self):

        self.logger.debug(self.taxitime_metric.summary)
        self.logger.debug(self.makespan_metric.summary)
        self.logger.debug(self.aircraft_count_metric.summary)
        self.logger.debug(self.conflict_metric.summary)
        self.logger.debug(self.gate_queue_metric.summary)
        self.logger.debug(self.schedule_metric.summary)
        self.logger.debug(self.execution_time_metric.summary)

    def save(self):

        self.save_tick_summary()
        self.save_schedule_summary()
        self.save_metrics()

    def save_tick_summary(self):

        c = self.aircraft_count_metric.counter.set_index("time")
        cr = self.conflict_metric.conflict_node.set_index("time")
        ca = self.conflict_metric.conflict_node_aircraft.set_index("time")
        cf = self.conflict_metric.conflict.set_index("time")
        qs = self.gate_queue_metric.gate_queue_size.set_index("time")

        stats = c.join(
            cr, lsuffix='_aircraft',
            rsuffix="_conflict_nodes"
        ).join(
            ca,
            rsuffix="_conflict_aircrafts"
        ).join(
            cf,
            rsuffix="_conflict"
        ).join(
            qs,
            rsuffix="_queue_size"
        )

        with pd.option_context("display.max_rows", None):
            self.logger.debug("\n" + str(stats))

        self.save_csv("tick", stats)
        self.save_fig("conflicts", cf)
        self.save_fig("gate-queue-size", qs)

    def save_schedule_summary(self):

        # Schedule metrics

        # Number of delays added
        dn = self.schedule_metric.delay_added.set_index("time")
        with pd.option_context("display.max_rows", None):
            self.logger.debug("\n" + str(dn))

        self.save_fig("delay_added", dn)

        # Execution time
        rst = self.execution_time_metric.rs_exec_time.set_index("time")
        with pd.option_context("display.max_rows", None):
            self.logger.debug("\n" + str(rst))

        self.save_fig("schedule_execution_time", rst)

        # Writes to one csv file
        stats = dn.join(rst)
        self.save_csv("schedule", stats)

    def save_csv(self, type_name, df):
        filename = "%s%s.csv" % (get_output_dir_name(), type_name)
        df.to_csv(filename)

    def save_fig(self, fig_name, df):
        filename = "%s%s.png" % (get_output_dir_name(), fig_name)
        df.plot(kind="line").get_figure().savefig(filename)

    def save_metrics(self):
        """
        Saves the output metrics of the simulation to a JSON file.
        """
        filename = "%smetrics.json" % get_output_dir_name()
        response = {
            "total_conflicts": self.conflict_metric.total_conflicts,
            "makespan": self.makespan_metric.makespan,
            "delay_added": self.schedule_metric.total_delay_time_added,
            "avg_queue_size": self.gate_queue_metric.avg_queue_size,
            "avg_reschedule_exec_time":
            self.execution_time_metric.avg_reschedule_exec_time
        }
        with open(filename, "w") as f:
            f.write(json.dumps(response))
        self.logger.info("Output metrics saved to %s" % filename)

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
