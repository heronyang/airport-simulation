# coding: utf-8
import pylab
import pandas as pd

CSV_FILE = "../batch_output/sfo-terminal-2-uc-xxl-partial/metrics.csv"
# INDEX = "simulation.reschedule_cycle"
INDEX = "uncertainty.prob_hold"

def main():

    data = pd.read_csv(CSV_FILE).set_index(INDEX)

    # Plot delay
    pylab.plot(data["avg_n_delay"], '-.', label="Total Delay")
    pylab.plot(data["avg_n_scheduler_delay"], '--', label="Scheduler Delay")
    pylab.plot(data["avg_n_uncertainty_delay"], ':',
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


if __name__ == "__main__":
    main()
