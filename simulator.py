#!/usr/bin/env python3
"""Simulator is the entry point for running a single simulation or a batch of
simulations.

Example:

    To run a single simulation, use an experimental plan under folder `plans`:

        $ ./simulator.py -f plans/base.yaml

    To run a batch of simulations, use a batch experimental plan under folder
    `batch_plans`:

        $ ./simulator.py -f batch_plans/sfo-terminal-2-uc.yaml

Output:

    Simulation results including output metrics, figures, and logs are stored
    under `output` folder with the name specified in the experimental plan. For
    batch runs, a bunch of folders under `output` are created and a folder
    under `batch_output` is created as well for storing summarized metrics and
    figures of the batch runs.

Definition:

    We define a `simulation` or a `simulation run` as the simulation of a day
    under the same parameters (this matches to an experimental plan under
    `plans`). We also define `sample times` as the number of simulations runs
    we execute under the same parameters for retrieving the average output
    metrics. Then, we define a `batch run` or a `batch execution` as multiple
    simulation runs that may or may not involve different parameters used per
    simulation run depends on the `sample times` (this matches to a batch
    experimental plan under `batch_plans`).

"""

from subprocess import call

import os
import sys
import time
import logging
import argparse
import pandas as pd
import numpy
import coloredlogs

from simulation import Simulation, SimulationException
from clock import ClockException
from config import Config as cfg
from utils import get_output_dir_name, get_batch_plan_name
from reporter import save_batch_result, save_failed_num


# TODO: Streaming Visualization
# TODO: make it class-based


def main():
    """Main function of the simulator."""

    __init_params()

    if cfg.params["batch"]:
        print("Starting the simulation in batch mode")
        run_batch()
    else:
        print("Starting the simulation")
        run()


def __init_params():
    # Parses argv
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--plan-filepath",
                        help="Filepath of the experiment plan",
                        required=True)

    # Loads experiment parameters into cfg
    cfg.load_plan(parser.parse_args().plan_filepath)


def __init_logger():
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
        sys.exit(1)

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
    """Executes a batch run given the name of this launch, the sample times
    value, the experimental variable name and the experimental variable value
    range specified in the configuration.
    """

    name = cfg.params["name"]
    times = cfg.params["simulator"]["times"]
    expr_var_name = cfg.params["batch"]
    expr_var_range = __get_expr_var_range(expr_var_name)

    logs = pd.DataFrame(columns=["expr_var", "failed", "nth"])

    if len(expr_var_range) < 2:
        raise Exception("Invalid configuration on expr_var_range")

    for expr_var in expr_var_range:
        for nth in range(times):
            run_wrapper(expr_var_name, expr_var, name, logs, nth=nth)

    save_batch_result(name, expr_var_name, expr_var_range, logs, times)
    print("Saved result")


def run_wrapper(expr_var_name, expr_var, name, logs, nth):
    """A wrapper for running a simulation for a batch run by setting up the
    experimental variable, counting the number of failures, and logging the
    execution time.
    """

    print("Running simulation with %s = %f (nth = %d)"
          % (expr_var_name, expr_var, nth))
    __set_expr_var(expr_var_name, expr_var)
    __set_plan_name(name, expr_var, nth)

    failed = 0
    while True:
        try:
            start = time.time()
            run()
        except SimulationException:
            failed += 1
            save_failed_num(name, expr_var, nth, failed)
            print("Conflict found, abort this simulation run")
            if not cfg.params["simulator"]["try_until_success"]:
                print("Gave up trying nth = %d" % nth)
                break
        else:
            print("Finished simulation with %s = %f, time %s seconds, nth = %d"
                  % (expr_var_name, expr_var, time.time() - start, nth))
            break
    save_failed_num(name, expr_var, nth, failed)
    logs.loc[len(logs)] = [expr_var, failed, nth]


def __get_expr_var_range(expr_var_name):
    # Finds the string value of the experimental field
    params = cfg.params
    expr_var_name_layer = expr_var_name.split(".")
    while expr_var_name_layer:
        params = params[expr_var_name_layer[0]]
        expr_var_name_layer = expr_var_name_layer[1:]

    # Parses the string representation in range
    range_raw = params
    (start, end, step) = range_raw.split(":")
    return numpy.arange(float(start), float(end), float(step))


def __set_expr_var(expr_var_name, expr_var):
    # Setup the experimental variable
    params = cfg.params
    expr_var_name_layer = expr_var_name.split(".")
    while len(expr_var_name_layer) > 1:
        params = params[expr_var_name_layer[0]]
        expr_var_name_layer = expr_var_name_layer[1:]
    params[expr_var_name_layer[0]] = expr_var


def __set_plan_name(name, expr_var, nth):
    cfg.params["name"] = get_batch_plan_name(name, expr_var, nth)


def run():
    """Executes a single simulation by initializing a `Simulation` and call its
    `tick()` function util the Clock` object raises an `ClockException`
    indicating the end of a day.
    """

    logger = __init_logger()

    if cfg.params["simulator"]["scenario_regeneration"]:
        logger.info("Generating scenario files")
        __regenerate_scenario()
        logger.info("Scenario files generated")

    simulation = Simulation()

    # Starts to tick periodically
    pause_time = cfg.params["simulator"]["pause_time"]
    try:
        while True:
            simulation.tick()

            # TODO: Streaming Visualization
            # TODO: yield state here

            if pause_time != 0:
                time.sleep(pause_time)
    except KeyboardInterrupt:
        logger.debug("Caught keyboard interrupt, simulation exits")
    except ClockException:
        logger.debug("Simulation ends")
    except SimulationException as exception:
        logger.error("Conflict found in the airport, abort")
        raise exception


def __regenerate_scenario():
    dir_path = cfg.DATA_GENERATION_DIR_PATH % cfg.params["airport"]
    current_dir = os.getcwd()
    os.chdir(dir_path)
    call(["./generate_scenario.py"])
    os.chdir(current_dir)


if __name__ == "__main__":
    main()
