"""`Analyst` contains a list of metrics and the observations happens in each
specific event such as tick or schedule. In these events, we update the metric
with the new information from the simulation. `Analyst` also summarizes and
generates the metrics files into disk which can be triggered at the end of a
simulation.
"""
import logging
import json
import matplotlib.pyplot as plt
import pandas as pd

from utils import get_time_delta, get_output_dir_name
from config import Config


class TaxitimeMetric():
    """`TaxitimeMetric` logs the taxi-time of all aircrafts in the simulation.
    We define the taxi time as the time an aircraft locates in the airport
    but is not parked at the gate.
    """

    def __init__(self, sim_time):

        self.moving_aircraft_count_on_tick = 0
        self.sim_time = sim_time

    def update_on_tick(self, aircrafts, scenario):
        """Updates the metric with the current aircrafts states and the
        scenario.
        """

        for aircraft in aircrafts:
            # If an aircraft is not close to its gate, it's on its taxiway
            flight = scenario.get_flight(aircraft)
            if not aircraft.location.is_close_to(flight.from_gate):
                self.moving_aircraft_count_on_tick += 1

    @property
    def taxi_time(self):
        """Returns the sum of the taxi time we've observed."""
        return self.moving_aircraft_count_on_tick * self.sim_time

    @property
    def summary(self):
        """Returns a summary string of this metric."""
        return "Taxitime: %d seconds" % self.taxi_time


class MakespanMetric():
    """`MakespanMetric` logs the makespan of a simulation. We define makespan
    as the time period between the first aircraft and the last aircraft we've
    observed during a simulation.
    """

    def __init__(self):

        self.aircraft_first_time = None
        self.aircraft_last_time = None

    def update_on_tick(self, aircrafts, now):
        """Updates the metrics with all active aircrafts."""

        if not aircrafts:
            return

        if self.aircraft_first_time is None:
            self.aircraft_first_time = now
        self.aircraft_last_time = now

    @property
    def __is_ready(self):
        return self.aircraft_first_time and self.aircraft_last_time

    @property
    def makespan(self):
        """Returns the makespan value."""
        return (get_time_delta(self.aircraft_last_time,
                               self.aircraft_first_time)
                if self.__is_ready else 0)

    @property
    def summary(self):
        """Returns a summary string of this metric."""

        if not self.__is_ready:
            return "Makespan: insufficient data"

        return "Makespan: %d seconds" % self.makespan


class AircraftCountMetric():
    """`AircraftCountMetric` logs the number of active aircrafts in the
    simulation.
    """

    def __init__(self):
        self.counter = pd.DataFrame(columns=["count"])

    def update_on_tick(self, aircrafts, now):
        """Updates the metrics with all active aircrafts."""
        self.counter.set_value(now, "count", len(aircrafts))

    @property
    def avg_n_aircrafts(self):
        """Returns the average number of aircrafts."""
        return self.counter["count"].mean()

    @property
    def summary(self):
        """Returns a summary string of this metric."""

        if not self.counter:
            return "Aircraft count: insufficient data"

        cnt = self.counter
        return ("Aircraft count: top %d low %d mean %d remaining %d" %
                (cnt.max(), cnt.min(), cnt.mean(), cnt.iloc[-1]))


class ConflictMetric():
    """`ConflictMetric` logs the number of conflicts in the simulation."""

    def __init__(self):
        self.conflict = pd.DataFrame(columns=["count"])

    def update_on_tick(self, conflicts, now):
        """Updates the metric with the conflicts observed in a tick."""
        self.conflict.set_value(now, "count", len(conflicts))

    @property
    def conflicts(self):
        """Returns the number of conflicts."""
        return self.conflict["count"].sum()

    @property
    def summary(self):
        """Returns a summary string of this metric."""

        if not self.conflicts:
            return "Conflict: insufficient data"

        cnf = self.conflict
        return (
            "Conflict: top %d low %d mean %d" %
            (cnf.max(), cnf.min(), cnf.mean())
        )


class GateQueueMetric():
    """`GateQueueMetric` logs the size of the queues at gate."""

    def __init__(self):
        self.gate_queue_size = pd.DataFrame(columns=["size"])

    def update_on_tick(self, airport, now):
        """Updates the metric with the airport state."""
        self.gate_queue_size.set_value(
            now, "size", sum([len(q) for q in airport.gate_queue.values()]))

    @property
    def avg_queue_size(self):
        """Returns the average size of the queue among the queue."""
        return self.gate_queue_size["size"].mean()

    @property
    def summary(self):
        """Returns a summary string of this metric."""

        if not self.gate_queue_size:
            return "Gate Queue: insufficient data"

        queue_size = self.gate_queue_size
        return "Gate Queue: top %d low %d mean %d" % (
            queue_size.max(), queue_size.min(), queue_size.mean()
        )


class ExecutionTimeMetric():
    """`ExecutionTimeMetric` logs the execution time taken each time the
    scheduler schedules.
    """

    def __init__(self):
        # Reschedule execution time
        self.rs_exec_time = pd.DataFrame(columns=["rs_exec_time"])

    def update_on_reschedule(self, rs_exec_time, now):
        """Updates the metric with the execution time taken for scheduling."""
        self.rs_exec_time.set_value(now, "rs_exec_time", rs_exec_time)

    @property
    def avg_reschedule_exec_time(self):
        """Returns the reschedule execution time."""
        return self.rs_exec_time["rs_exec_time"].mean()

    @property
    def summary(self):
        """Returns a summary string of this metric."""

        if not self.rs_exec_time:
            return "Execution Time: insufficient data"

        rst = self.rs_exec_time

        return "Reschedule execution time: top %d low %d mean %d" % (
            rst.max(), rst.min(), rst.mean()
        )


class DelayMetric():
    """`DelayMetric` logs the delay of each aircraft encountered in each tick.
    """

    def __init__(self):
        self.delay = pd.DataFrame(
            columns=["n_scheduler_delay", "n_uncertainty_delay"]
        )

    def update_on_tick(self, aircrafts, now):
        """Updates the metric with the active aircrafts."""

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
    def n_scheduler_delay(self):
        """Returns the number of the scheduler delays."""
        # Average number of delay added by the scheduler per tick
        return self.delay["n_scheduler_delay"].sum()

    @property
    def n_uncertainty_delay(self):
        """Returns the number of uncertainty delays."""
        # Average number of delay added by the uncertainty module per tick
        return self.delay["n_uncertainty_delay"].sum()

    @property
    def n_delay(self):
        """Returns the total number of delays (that is, the scheduler delay and
        the uncertainty delay).
        """
        return self.n_scheduler_delay + self.n_uncertainty_delay

    @property
    def summary(self):
        """Returns a summary string of this metric."""

        if not self.delay:
            return "Delay: insufficient data"

        delay = self.delay
        return "Delay: top %d low %d mean %d" % (delay.max(),
                                                 delay.min(), delay.mean())


class Analyst:
    """`Analyst` maintains multiple metrics by observing the simulation states
    on tick and schedule events, then generates the final output metrics to
    string or file.
    """

    def __init__(self, simulation):

        self.logger = logging.getLogger(__name__)
        self.airport_name = simulation.airport.name

        sim_time = simulation.clock.sim_time

        self.taxitime_metric = TaxitimeMetric(sim_time)
        self.makespan_metric = MakespanMetric()
        self.aircraft_count_metric = AircraftCountMetric()
        self.conflict_metric = ConflictMetric()
        self.gate_queue_metric = GateQueueMetric()
        self.execution_time_metric = ExecutionTimeMetric()
        self.delay_metric = DelayMetric()

        self.__save_airport_name()

    def observe_on_tick(self, simulation):
        """Observe the simulation state on tick."""

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

    def observe_on_reschedule(self, simulation):
        """Observe the simulation state on reschedule."""

        now = simulation.now
        self.execution_time_metric.update_on_reschedule(
            simulation.last_schedule_exec_time, now)

    def print_summary(self):
        """Prints the summary."""

        self.logger.debug(self.taxitime_metric.summary)
        self.logger.debug(self.makespan_metric.summary)
        self.logger.debug(self.aircraft_count_metric.summary)
        self.logger.debug(self.conflict_metric.summary)
        self.logger.debug(self.gate_queue_metric.summary)
        self.logger.debug(self.execution_time_metric.summary)
        self.logger.debug(self.delay_metric.summary)

    def save(self):
        """Saves the output metrics to file."""

        self.__save_tick_summary()
        self.__save_schedule_summary()
        self.__save_metrics()

        plt.close('all')

    def __save_tick_summary(self):

        cnt = self.aircraft_count_metric.counter
        cnf = self.conflict_metric.conflict
        queue_size = self.gate_queue_metric.gate_queue_size
        delay = self.delay_metric.delay

        stats = cnt.join(
            cnf,
            rsuffix="_conflict"
        ).join(
            queue_size,
            rsuffix="_queue_size"
        ).join(
            delay
        )

        with pd.option_context("display.max_rows", None):
            self.logger.debug("\n" + str(stats))

        save_csv("tick", stats)
        save_fig("conflicts", cnf, "line")
        save_fig("gate_queue_size", queue_size, "line")
        save_fig("delay", delay, "line")

    def __save_schedule_summary(self):

        # Execution time
        rst = self.execution_time_metric.rs_exec_time
        with pd.option_context("display.max_rows", None):
            self.logger.debug("\n" + str(rst))

        save_fig("schedule_execution_time", rst, "line")

        # Writes to one csv file
        save_csv("schedule", rst)

    def __save_metrics(self):
        """Saves the output metrics of the simulation to a JSON file."""
        filename = "%smetrics.json" % get_output_dir_name()
        response = {
            "avg_active_aircrafts": self.aircraft_count_metric.avg_n_aircrafts,
            "conflicts": self.conflict_metric.conflicts,
            "makespan": self.makespan_metric.makespan,
            "avg_queue_size": self.gate_queue_metric.avg_queue_size,
            "avg_reschedule_exec_time":
            self.execution_time_metric.avg_reschedule_exec_time,
            "n_delay": self.delay_metric.n_delay,
            "n_scheduler_delay":
            self.delay_metric.n_scheduler_delay,
            "n_uncertainty_delay":
            self.delay_metric.n_uncertainty_delay
        }
        with open(filename, "w") as fout:
            fout.write(json.dumps(response, indent=4))
        self.logger.info("Output metrics saved to %s", filename)

    def __save_airport_name(self):
        filename = "%sairport.txt" % get_output_dir_name()
        with open(filename, "w") as fout:
            fout.write(self.airport_name)
        self.logger.info("Airport name logged to %s", filename)

    def __getstate__(self):
        attrs = dict(self.__dict__)
        del attrs["logger"]
        return attrs

    def __setstate__(self, attrs):
        self.__dict__.update(attrs)


def save_csv(type_name, dataframe):
    """Saves the given dataframe to a csv file."""
    filename = "%s%s.csv" % (get_output_dir_name(), type_name)
    dataframe.to_csv(filename)


def save_fig(fig_name, dataframe, kind):
    """Saves the given dataframe to a figure file."""
    filename = "%s%s.png" % (get_output_dir_name(), fig_name)
    plt.clf()
    plt.figure(figsize=Config.OUTPUT_FIG_SIZE)
    dataframe.plot(kind=kind)
    plt.tight_layout()
    plt.savefig(filename, dpi=Config.OUTPUT_FIG_DPI)
