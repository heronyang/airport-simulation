#!/usr/bin/env python3
# coding: utf-8
import pylab
import pandas as pd

ROOT_DIR = "../batch_output/sfo-terminal-2-rt-success/"
METRICS_CSV = ROOT_DIR + "metrics.csv"
FAILED_CSV = ROOT_DIR + "logs.csv"
INDEX = "simulation.reschedule_cycle"
# INDEX = "uncertainty.prob_hold"


def main():

    data = pd.read_csv(METRICS_CSV).set_index(INDEX)

    # Plot delay
    pylab.plot(data["n_delay"], '-.', label="Total Delay")
    pylab.plot(data["n_scheduler_delay"], '--', label="Scheduler Delay")
    pylab.plot(data["n_uncertainty_delay"], ':',
               label="Uncertainty Delay")
    pylab.legend()
    pylab.savefig("delay.png")
    pylab.clf()

    # Plot queue size
    pylab.plot(data["avg_queue_size"], '-', label="Queue Size")
    pylab.legend()
    pylab.savefig("queue_size.png")
    pylab.clf()

    # Plot schedule execution time
    pylab.plot(data["avg_reschedule_exec_time"], '-',
               label="Schedule Execution Time")
    pylab.legend()
    pylab.savefig("schedule_exec_time.png")
    pylab.clf()

    # Plot failure
    failed = pd.read_csv(FAILED_CSV)[["expr_var", "failed"]]
    failed_mean_count = failed.groupby("expr_var").agg(["mean", "count"])
    pylab.plot(failed_mean_count["failed"]["mean"], "-", label="Portion of the"
               + " early-terminated simulations")
    pylab.legend()
    pylab.savefig("failure.png")
    pylab.clf()


if __name__ == "__main__":
    main()
