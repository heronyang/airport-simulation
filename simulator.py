#!/usr/bin/env python3
import os
import sys
import time
import numpy
import logging
import coloredlogs
import argparse
import threading
import traceback
import pandas as pd

from simulation import Simulation, SimulationException
from clock import ClockException
from config import Config as cfg
from utils import get_output_dir_name, get_batch_plan_name
from reporter import save_batch_result
from subprocess import call

logger = None

def main():

    init_params()

    if cfg.params["batch"]:
        print("Starting the simulation in batch mode")
        run_batch()
    else:
        print("Starting the simulation")
        run()


def init_params():

    # Parses argv
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--plan-filepath",
                        help="Filepath of the experiment plan",
                        required=True)

    # Loads experiment parameters into cfg
    cfg.load_plan(parser.parse_args().plan_filepath)


def init_logger():

    # Removes previous handler
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    levels = {
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    try:
        level = levels[cfg.params["logger"]["level"]]
    except KeyError:
        logger.error("Unknown logging level")
        os._exit(1)

    if cfg.params["logger"]["file"] or cfg.params["batch"] is not None:
        log_filename = get_output_dir_name() + "log"
        try:
            os.remove(log_filename)
        except OSError:
            pass
        logging.basicConfig(
            format=cfg.LOG_FORMAT,
            filename=log_filename,
            level=level
        )

    else:
        coloredlogs.install(level=level, fmt=cfg.LOG_FORMAT)

    return logging.getLogger(__name__)

def run_batch():

    name = cfg.params["name"]
    times = cfg.params["simulator"]["times"]
    expr_var_name = cfg.params["batch"]
    expr_var_range = get_expr_var_range(expr_var_name)

    logs = pd.DataFrame(columns=["expr_var", "failed", "nth"])

    if len(expr_var_range) < 2:
        raise Exception("Invalid configuration on expr_var_range")

    for expr_var in expr_var_range:
        if times <= 1:
            run_wrapper(expr_var_name, expr_var, name, logs, nth=None)
        else:
            for t in range(times):
                run_wrapper(expr_var_name, expr_var, name, logs, nth=t)

    save_batch_result(name, expr_var_name, expr_var_range, logs, times)
    print("Saved result")

done = False

def run_wrapper(expr_var_name, expr_var, name, logs, nth):

    global done

    print("Running simulation with %s = %f (nth = %d)"
          % (expr_var_name, expr_var, nth))
    done = False
    set_expr_var(expr_var_name, expr_var)
    set_plan_name(name, expr_var, nth)

    failed = 0
    while True:
        try:
            start = time.time()
            run()
        except SimulationException:
            failed += 1
            print("Conflict found, abort this simulation run")
        else:
            print("Finished simulation with %s = %f, time %s seconds, nth = %d"
                  % (expr_var_name, expr_var, time.time() - start, nth))
            break
    logs.loc[len(logs)] = [expr_var, failed, nth]

def get_expr_var_range(expr_var_name):

    # Finds the string value of the experimental field
    c = cfg.params
    expr_var_name_layer = expr_var_name.split(".")
    while len(expr_var_name_layer) > 0:
        c = c[expr_var_name_layer[0]]
        expr_var_name_layer = expr_var_name_layer[1:]

    # Parses the string representation in range
    range_raw = c
    (start, end, step) = range_raw.split(":")
    return numpy.arange(float(start), float(end), float(step))

def set_expr_var(expr_var_name, expr_var):

    # Setup the experimental variable
    c = cfg.params
    expr_var_name_layer = expr_var_name.split(".")
    while len(expr_var_name_layer) > 1:
        c = c[expr_var_name_layer[0]]
        expr_var_name_layer = expr_var_name_layer[1:]
    c[expr_var_name_layer[0]] = expr_var

def set_plan_name(name, expr_var, nth):
    cfg.params["name"] = get_batch_plan_name(name, expr_var, nth)

def run():

    global logger
    logger = init_logger()

    if cfg.params["simulator"]["scenario_regeneration"]:
        regenerate_scenario()

    simulation = Simulation()

    global done

    # Starts to tick periodically
    pause_time = cfg.params["simulator"]["pause_time"]
    try:
        while not done:
            simulation.tick()
            if pause_time != 0:
                time.sleep(pause_time)
    except KeyboardInterrupt:
        logger.debug("Caught keyboard interrupt, simulation exits")
    except ClockException:
        logger.debug("Simulation ends")
    except SimulationException:
        logger.error("Conflict found in the airport, abort")
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("Simulation exists on unexpected error")
        os._exit(-1)

def regenerate_scenario():
    logger.info("Generating scenario files")
    dir_path = cfg.DATA_GENERATION_DIR_PATH % cfg.params["airport"]
    current_dir = os.getcwd()
    os.chdir(dir_path)
    call(["./generate_scenario.py"])
    os.chdir(current_dir)
    logger.info("Scenario files generated")

if __name__ == "__main__":
    main()
