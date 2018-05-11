"""Reporter provides helper functions for saving the final results of the batch
simulation runs into csv files or plots.
"""
import os
import shutil
import json
import pylab
import pandas as pd
import matplotlib.pyplot as plt
from config import Config as cfg
from utils import get_batch_plan_name


def save_batch_result(name, expr_var_name, expr_var_range, logs, times):
    """Saves the batch result into files.
    Parameters:
        expr_var_name: the name of the experimental variable
        expr_var_range: the value range of the experimental variable
        logs: the number of failures stored in a dataframe
        times: the number of sample per setting
    """

    metrics_filename = "/metrics.json"

    m_metrics = [__get_blank_metrics(expr_var_name) for _ in range(times)]

    for expr_var in expr_var_range:
        for nth in range(times):
            filename = cfg.OUTPUT_DIR + get_batch_plan_name(
                name, expr_var, nth) + metrics_filename
            try:
                m_metrics[nth] = __append_expr_output(
                    filename, expr_var_name, expr_var, m_metrics[nth])
            except FileNotFoundError:
                print("Skipped loading %s for report" % filename)

    metrics = pd.concat(m_metrics).set_index(expr_var_name)
    metrics = metrics.groupby(metrics.index).mean()

    output_dir = cfg.BATCH_OUTPUT_DIR + name + "/"
    __setup_output_dir(output_dir)
    __save_metrics(metrics, output_dir)
    __save_logs(logs, output_dir)


def __get_blank_metrics(expr_var_name):
    return pd.DataFrame(columns=[
        expr_var_name,
        "avg_active_aircrafts",
        "conflicts",
        "makespan",
        "avg_queue_size",
        "avg_reschedule_exec_time",
        "n_delay",
        "n_scheduler_delay",
        "n_uncertainty_delay"
    ])


def __append_expr_output(filename, expr_var_name, expr_var, metrics):
    with open(filename) as fin:
        table = json.load(fin)
        metrics = metrics.append({
            expr_var_name: expr_var,
            "avg_active_aircrafts": table["avg_active_aircrafts"],
            "conflicts": table["conflicts"],
            "makespan": table["makespan"],
            "avg_queue_size": table["avg_queue_size"],
            "avg_reschedule_exec_time": table["avg_reschedule_exec_time"],
            "n_delay": table["n_delay"],
            "n_scheduler_delay": table["n_scheduler_delay"],
            "n_uncertainty_delay": table["n_uncertainty_delay"]
        }, ignore_index=True)
    return metrics


def __save_metrics_bk(metrics, output_dir):
    metrics.to_csv(output_dir + "metrics.csv")
    for col in list(metrics):
        plt.clf()
        plt.figure(figsize=cfg.OUTPUT_FIG_SIZE)
        filename = output_dir + col + ".png"
        metrics[col].plot(kind="line")
        plt.tight_layout()
        plt.savefig(filename, dpi=cfg.OUTPUT_FIG_DPI)
    plt.close('all')


def __save_metrics(metrics, output_dir):

    # Saves to a CSV file
    metrics.to_csv(output_dir + "metrics.csv")

    # Saves plots

    # Plot delay
    pylab.plot(metrics["n_delay"], '-.', label="Total Delay")
    pylab.plot(metrics["n_scheduler_delay"], '--', label="Scheduler Delay")
    pylab.plot(metrics["n_uncertainty_delay"], ':',
               label="Uncertainty Delay")
    pylab.legend()
    pylab.savefig(output_dir + "delay.png")
    pylab.clf()

    # Plot queue size
    pylab.plot(metrics["avg_queue_size"], '-', label="Queue Size")
    pylab.legend()
    pylab.savefig(output_dir + "queue_size.png")
    pylab.clf()

    # Plot schedule execution time
    pylab.plot(metrics["avg_reschedule_exec_time"], '-',
               label="Schedule Execution Time")
    pylab.legend()
    pylab.savefig(output_dir + "schedule_exec_time.png")
    pylab.clf()


def __setup_output_dir(output_dir):
    # Removes the folder if it's already exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    # Creates a brand new folder
    os.makedirs(output_dir)


def __save_logs(logs, output_dir):

    if logs is None:
        print("Logs are empty")
        return

    # Saves to csv file
    logs.to_csv(output_dir + "logs.csv")

    # Saves the plot
    failed = logs[["expr_var", "failed"]]
    failed_mean_count = failed.groupby("expr_var").agg(["mean", "count"])
    pylab.plot(failed_mean_count["failed"]["mean"], "-", label="Portion of the"
               + " early-terminated simulations")
    pylab.legend()
    pylab.savefig(output_dir + "failure.png")
    pylab.clf()


def save_failed_num(name, expr_var, nth, failed):
    """Saves the number of failed simulation runs into a file."""
    filename = cfg.OUTPUT_DIR +\
        get_batch_plan_name(name, expr_var, nth) + "/failed"
    with open(filename, "w") as fout:
        fout.write(str(failed))
