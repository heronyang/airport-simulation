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
from clock import ClockException
from config import Config as cfg
from utils import get_output_dir_name

logger = logging.getLogger(__name__)


def main():

    init_params()
    init_logger()

    logger.info("Starting the simulation")
    run(Simulation(), None)


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

    if cfg.params["logger"]["file"]:
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


done = False
def run(simulation, monitor):

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
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("Simulation exists on unexpected error")
        os._exit(-1)


if __name__ == "__main__":
    main()
