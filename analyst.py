import logging
import pandas as pd
import json
import matplotlib.pyplot as plt

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
        self.counter = pd.DataFrame(columns=["count"])

    def update_on_tick(self, aircrafts, now):
        self.counter.set_value(now, "count", len(aircrafts))

    @property
    def summary(self):

        if len(self.counter) == 0:
            return "Aircraft count: insufficient data"

        c = self.counter
        return ("Aircraft count: top %d low %d mean %d remaining %d" %
                (c.max(), c.min(), c.mean(), c.iloc[-1]))


class ConflictMetric():

    def __init__(self):
        self.conflict = pd.DataFrame(columns=["count"])

    def update_on_tick(self, conflicts, now):
        self.conflict.set_value(now, "count", len(conflicts))

    @property
    def conflicts(self):
        return self.conflict["count"].sum()

    @property
    def summary(self):

        if len(self.conflict) == 0:
            return "Conflict: insufficient data"

        cf = self.conflict
        return (
            "Conflict: top %d low %d mean %d" % (cf.max(), cf.min(), cf.mean())
        )


class GateQueueMetric():

    def __init__(self, surface):
        self.gate_queue_size = pd.DataFrame(columns=["size"])

    def update_on_tick(self, airport, now):
        self.gate_queue_size.set_value(
            now, "size", sum([len(q) for q in airport.gate_queue.values()]))

    @property
    def avg_queue_size(self):
        return self.gate_queue_size["size"].mean()

    @property
    def summary(self):

        if len(self.gate_queue_size) == 0:
            return "Gate Queue: insufficient data"

        qs = self.gate_queue_size

        return "Gate Queue: top %d low %d mean %d" % (
            qs.max(), qs.min(), qs.mean()
        )


class ExecutionTimeMetric():

    def __init__(self):
        # Reschedule execution time
        self.rs_exec_time = pd.DataFrame(columns=["rs_exec_time"])

    def update_on_reschedule(self, rs_exec_time, now):
        self.rs_exec_time.set_value(now, "rs_exec_time", rs_exec_time)

    @property
    def avg_reschedule_exec_time(self):
        return self.rs_exec_time["rs_exec_time"].mean()

    @property
    def summary(self):

        if len(self.rs_exec_time) == 0:
            return "Execution Time: insufficient data"

        rst = self.rs_exec_time

        return "Reschedule execution time: top %d low %d mean %d" % (
            rst.max(), rst.min(), rst.mean()
        )


class DelayMetric():

    def __init__(self):
        self.delay = pd.DataFrame(
            columns=["n_scheduler_delay", "n_uncertainty_delay"]
        )

    def update_on_tick(self, aircrafts, now):

        n_scheduler_delay = len([
            aircraft for aircraft in aircrafts
            if aircraft.itinerary is not None and
            aircraft.itinerary.is_delayed_by_scheduler
        ])

        n_uncertainty_delay = len([
            aircraft for aircraft in aircrafts
            if aircraft.itinerary is not None and
            aircraft.itinerary.is_delayed_by_uncertainty
        ])

        self.delay.set_value(now, "n_scheduler_delay", n_scheduler_delay)
        self.delay.set_value(now, "n_uncertainty_delay", n_uncertainty_delay)

    @property
    def avg_n_scheduler_delay(self):
        # Average number of delay added by the scheduler per tick
        return self.delay["n_scheduler_delay"].mean()

    @property
    def avg_n_uncertainty_delay(self):
        # Average number of delay added by the uncertainty module per tick
        return self.delay["n_uncertainty_delay"].mean()

    @property
    def avg_n_delay(self):
        return self.avg_n_scheduler_delay + self.avg_n_uncertainty_delay

    @property
    def summary(self):

        if len(self.delay) == 0:
            return "Delay: insufficient data"

        d = self.delay
        return "Delay: top %d low %d mean %d" % (d.max(), d.min(), d.mean())


class Analyst:

    def __init__(self, simulation):

        self.logger = logging.getLogger(__name__)
        self.airport_name = simulation.airport.code

        sim_time = simulation.clock.sim_time

        self.taxitime_metric = TaxitimeMetric(sim_time)
        self.makespan_metric = MakespanMetric()
        self.aircraft_count_metric = AircraftCountMetric()
        self.conflict_metric = ConflictMetric()
        self.gate_queue_metric = GateQueueMetric(simulation.airport.surface)
        self.execution_time_metric = ExecutionTimeMetric()
        self.delay_metric = DelayMetric()

        self.save_airport_name()

    def observe_on_tick(self, simulation):

        now = simulation.now
        airport = simulation.airport
        aircrafts = airport.aircrafts
        scenario = simulation.scenario
        conflicts = simulation.airport.conflicts

        self.taxitime_metric.update_on_tick(aircrafts, scenario)
        self.makespan_metric.update_on_tick(aircrafts, now)
        self.aircraft_count_metric.update_on_tick(aircrafts, now)
        self.conflict_metric.update_on_tick(conflicts, now)
        self.gate_queue_metric.update_on_tick(airport, now)
        self.delay_metric.update_on_tick(aircrafts, now)

    def observe_on_reschedule(self, schedule, simulation):
        now = simulation.now
        self.execution_time_metric.update_on_reschedule(
            simulation.last_schedule_exec_time, now)

    def print_summary(self):

        self.logger.debug(self.taxitime_metric.summary)
        self.logger.debug(self.makespan_metric.summary)
        self.logger.debug(self.aircraft_count_metric.summary)
        self.logger.debug(self.conflict_metric.summary)
        self.logger.debug(self.gate_queue_metric.summary)
        self.logger.debug(self.execution_time_metric.summary)
        self.logger.debug(self.delay_metric.summary)

    def save(self):

        self.save_tick_summary()
        self.save_schedule_summary()
        self.save_metrics()

        plt.close('all')

    def save_tick_summary(self):

        c = self.aircraft_count_metric.counter
        cf = self.conflict_metric.conflict
        qs = self.gate_queue_metric.gate_queue_size
        delay = self.delay_metric.delay

        stats = c.join(
            cf,
            rsuffix="_conflict"
        ).join(
            qs,
            rsuffix="_queue_size"
        ).join(
            delay
        )

        with pd.option_context("display.max_rows", None):
            self.logger.debug("\n" + str(stats))

        self.save_csv("tick", stats)
        self.save_fig("conflicts", cf, "line")
        self.save_fig("gate_queue_size", qs, "line")
        self.save_fig("delay", delay, "line")

    def save_schedule_summary(self):

        # Execution time
        rst = self.execution_time_metric.rs_exec_time
        with pd.option_context("display.max_rows", None):
            self.logger.debug("\n" + str(rst))

        self.save_fig("schedule_execution_time", rst, "line")

        # Writes to one csv file
        self.save_csv("schedule", rst)

    def save_csv(self, type_name, df):
        filename = "%s%s.csv" % (get_output_dir_name(), type_name)
        df.to_csv(filename)

    def save_fig(self, fig_name, df, kind):
        filename = "%s%s.png" % (get_output_dir_name(), fig_name)
        plt.clf()
        plt.figure(figsize=Config.OUTPUT_FIG_SIZE)
        df.plot(kind=kind)
        plt.tight_layout()
        plt.savefig(filename, dpi=Config.OUTPUT_FIG_DPI)

    def save_metrics(self):
        """
        Saves the output metrics of the simulation to a JSON file.
        """
        filename = "%smetrics.json" % get_output_dir_name()
        response = {
            "conflicts": self.conflict_metric.conflicts,
            "makespan": self.makespan_metric.makespan,
            "avg_queue_size": self.gate_queue_metric.avg_queue_size,
            "avg_reschedule_exec_time":
            self.execution_time_metric.avg_reschedule_exec_time,
            "avg_n_delay": self.delay_metric.avg_n_delay,
            "avg_n_scheduler_delay":
            self.delay_metric.avg_n_scheduler_delay,
            "avg_n_uncertainty_delay":
            self.delay_metric.avg_n_uncertainty_delay
        }
        with open(filename, "w") as f:
            f.write(json.dumps(response, indent=4))
        self.logger.info("Output metrics saved to %s" % filename)

    def save_airport_name(self):
        filename = "%sairport.txt" % get_output_dir_name()
        with open(filename, "w") as f:
            f.write(self.airport_name)
        self.logger.info("Airport name logged to %s" % filename)

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
