#!/usr/bin/env python3
import os
import sys
import time
import logging
import coloredlogs
import argparse
import threading
import traceback

from simulation import Simulation
from monitor import Monitor
from clock import ClockException
from config import Config as cfg

logger = logging.getLogger(__name__)


def main():

    init_params()
    init_logger()

    if cfg.params["monitor"]["enabled"]:
        start_with_monitor()
    else:
        start()


def init_params():

    # Parses argv
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--plan-filepath",
                        help="Filepath of the experiment plan",
                        required=True)

    # Loads experiment parameters into cfg
    cfg.load_plan(parser.parse_args().plan_filepath)


def init_logger():

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

    coloredlogs.install(level=level, fmt=cfg.LOG_FORMAT)


def start():
    logger.info("Starting the simulation")
    run(Simulation(), None)


done = False


def start_with_monitor():

    global done

    if cfg.params["simulator"]["pause_time"] == 0:
        logger.error("Pause time can't be 0 if graphic display is enabled")
        os._exit(1)

    logger.info("Starting the simulation with monitor")

    # Initializes the simulation
    simulation = Simulation()

    # Initializes the monitor
    monitor = Monitor(simulation)

    # Runs simulation  (non-block)
    simulation_thread = threading.Thread(
        target=run, args=(simulation, monitor)
    )
    simulation_thread.start()

    # Runs monitor (block)
    monitor.start()
    logger.debug("Monitor ends")

    done = True


def run(simulation, monitor):

    global done

    # Starts to tick periodically
    pause_time = cfg.params["simulator"]["pause_time"]
    try:
        while not done:
            simulation.tick()
            if monitor:
                monitor.tick()
            if pause_time != 0:
                time.sleep(pause_time)
    except KeyboardInterrupt:
        logger.debug("Caught keyboard interrupt, simulation exits")
    except ClockException:
        logger.debug("Simulation ends")
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("Simulation exists on unexpected error")
        os._exit(-1)


if __name__ == "__main__":
    main()
