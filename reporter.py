import os
import shutil
import json
import pandas as pd
import matplotlib.pyplot as plt
from config import Config as cfg
from utils import get_batch_plan_name


def save_batch_result(name, expr_var_name, expr_var_range, logs, times):

    metrics_filename = "/metrics.json"

    if times < 2:

        # Reads and merges the metrics
        metrics = __get_blank_metrics(expr_var_name)

        for expr_var in expr_var_range:
            filename = cfg.OUTPUT_DIR + \
                    get_batch_plan_name(name, expr_var, None) +\
                    metrics_filename
            metrics = __append_expr_output(
                filename, expr_var_name, expr_var, metrics)

        # Saves the metrics onto disk
        metrics = metrics.set_index(expr_var_name)

    else:

        m_metrics = [__get_blank_metrics(expr_var_name) for _ in range(times)]

        for expr_var in expr_var_range:
            for nth in range(times):
                filename = cfg.OUTPUT_DIR + get_batch_plan_name(
                    name, expr_var, nth) + metrics_filename
                m_metrics[nth] = __append_expr_output(
                    filename, expr_var_name, expr_var, m_metrics[nth])
        metrics = pd.concat(m_metrics).set_index(expr_var_name)
        metrics = metrics.groupby(metrics.index).mean()

    output_dir = cfg.BATCH_OUTPUT_DIR + name + "/"
    setup_output_dir(output_dir)
    save_metrics(metrics, output_dir)
    save_logs(logs, times, output_dir)


def __get_blank_metrics(expr_var_name):
    return pd.DataFrame(columns=[
        expr_var_name,
        "conflicts",
        "makespan",
        "avg_queue_size",
        "avg_reschedule_exec_time",
        "avg_n_delay",
        "avg_n_scheduler_delay",
        "avg_n_uncertainty_delay"
    ])


def __append_expr_output(filename, expr_var_name, expr_var, metrics):
    with open(filename) as f:
        d = json.load(f)
        metrics = metrics.append({
            expr_var_name: expr_var,
            "conflicts": d["conflicts"],
            "makespan": d["makespan"],
            "avg_queue_size": d["avg_queue_size"],
            "avg_reschedule_exec_time": d["avg_reschedule_exec_time"],
            "avg_n_delay": d["avg_n_delay"],
            "avg_n_scheduler_delay": d["avg_n_scheduler_delay"],
            "avg_n_uncertainty_delay": d["avg_n_uncertainty_delay"]
        }, ignore_index=True)
    return metrics


def save_metrics(metrics, output_dir):
    metrics.to_csv(output_dir + "metrics.csv")
    for col in list(metrics):
        plt.clf()
        plt.figure(figsize=cfg.OUTPUT_FIG_SIZE)
        filename = output_dir + col + ".png"
        metrics[col].plot(kind="line")
        plt.tight_layout()
        plt.savefig(filename, dpi=cfg.OUTPUT_FIG_DPI)
    plt.close('all')


def setup_output_dir(output_dir):
    # Removes the folder if it's already exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    # Creates a brand new folder
    os.makedirs(output_dir)


def save_logs(logs, times, output_dir):

    if logs is None:
        print("Logs are empty")
        return

    # Calculates the failture rate
    d = logs.groupby(logs["expr_var"]).sum()
    d["failure_rate"] = d["failed"] / times

    # Saves to csv file
    logs.to_csv(output_dir + "logs.csv")

    # Plot the logs df
    plt.clf()
    plt.figure(figsize=cfg.OUTPUT_FIG_SIZE)
    filename = output_dir + "failure_rate.png"
    d["failure_rate"].plot(kind="line")
    plt.tight_layout()
    plt.savefig(filename, dpi=cfg.OUTPUT_FIG_DPI)
    plt.close('all')


def test():
    import numpy
    save_batch_result(
        "sfo-terminal-2-rt-s",
        "simulation.reschedule_cycle",
        numpy.arange(60.0, 151.0, 60.0),
        None,
        2
    )


if __name__ == "__main__":
    test()
