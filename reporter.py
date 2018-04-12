import os
import shutil
import json
import pandas as pd
import matplotlib.pyplot as plt
from config import Config as cfg

def save_batch_result(name, expr_var_name, expr_var_range):

    # Reads and merges the metrics
    metrics = pd.DataFrame(columns=[
        expr_var_name,
        "conflicts",
        "makespan",
        "delay_added",
        "avg_queue_size",
        "avg_reschedule_exec_time",
        "avg_n_delay",
        "avg_n_scheduler_delay",
        "avg_n_uncertainty_delay"
    ])

    for expr_var in expr_var_range:
        filename = cfg.OUTPUT_DIR + name + "-batch-" + str(expr_var) +\
                "/metrics.json"

        with open(filename) as f:
            d = json.load(f)
            metrics = metrics.append({
                expr_var_name: expr_var,
                "conflicts": d["conflicts"],
                "makespan": d["makespan"],
                "delay_added": d["delay_added"],
                "avg_queue_size": d["avg_queue_size"],
                "avg_reschedule_exec_time": d["avg_reschedule_exec_time"],
                "avg_n_delay": d["avg_n_delay"],
                "avg_n_scheduler_delay": d["avg_n_scheduler_delay"],
                "avg_n_uncertainty_delay": d["avg_n_uncertainty_delay"]
            }, ignore_index=True)

    # Saves the metrics onto disk
    metrics = metrics.set_index(expr_var_name)
    save_metrics(metrics, cfg.BATCH_OUTPUT_DIR + name + "/")

def save_metrics(metrics, output_dir):
    setup_output_dir(output_dir)
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

# import numpy
# save_batch_result("simple-continuous-uc", "uncertainty.hold_prob", numpy.arange(0.0, 0.8, 0.2))
