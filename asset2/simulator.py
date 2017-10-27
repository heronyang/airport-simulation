#!/usr/bin/env python3
import os
import sys
import time
import logging
import argparse
import threading
import traceback

from simulation import Simulation
from monitor import Monitor
from clock import ClockException
from config import Config

is_finished = False

# Logger
log_format = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] "\
        "%(message)s"
logging.basicConfig(level = logging.DEBUG, format = log_format)
logger = logging.getLogger(__name__)

def main():

    # Gets the arguments
    params = get_params()
    logger.debug("Parameters: %s" % params)

    if params.graphic:
        start_with_monitor(params)
    else:
        start(params)

def get_params():

    # Parses arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--airport", help = "IATA airport code",
                        required = True)
    parser.add_argument("-g", "--graphic", help = "Enable graphical monitor",
                        action = "store_true", default = False)

    parser.add_argument("-tp", "--tick-pause-time", type = int,
                        help = "Seconds paused between each tick in real world",
                        default = Config.DEFAULT_TICK_PAUSE_TIME)
    parser.add_argument("-ts", "--tick-sim-time", type = int,
                        help = "Seconds past between each tick in the " \
                        "simluated world",
                        default = Config.DEFAULT_TICK_SIM_TIME)
    parser.add_argument("-tr", "--reschedule-sim-time", type = int,
                       help = "Seconds past between scheduling requests in" \
                        "simulated world (seconds)",
                        default = Config.DEFAULT_SCHEDULE_SIM_TIME)

    return parser.parse_args()

def start(params):

    logger.debug("Starting the simulation")

    # Initializes the simulation
    simulation = Simulation(params.airport,
                            params.tick_sim_time,
                            params.reschedule_sim_time)
    run_simulation(simulation, params.tick_pause_time, None)


def start_with_monitor(params):

    logger.debug("Starting the simulation with monitor")

    global is_finished

    # Initializes the simulation
    simulation = Simulation(params.airport,
                            params.tick_sim_time,
                            params.reschedule_sim_time)

    # Initializes the monitor
    monitor = Monitor(simulation)

    # Runs simulation  (non-block)
    simulation_thread = threading.Thread(
        target = run_simulation,
        args = (simulation, params.tick_pause_time, monitor))
    simulation_thread.start()

    # Runs monitor (block)
    monitor.start()
    logger.debug("Monitor ends")

    is_finished = True

def run_simulation(simulation, pause_time, monitor):

    global is_finished

    # Starts to tick periodically
    try:
        while not is_finished:
            simulation.tick()
            if monitor:
                monitor.tick()
            time.sleep(pause_time)
    except KeyboardInterrupt:
        logger.debug("Caught keyboard interrupt, simulation exits")
    except ClockException:
        logger.debug("Simulation ends")
        # TODO: Should ask the simulation for performance metric here
    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.debug("Simulation exists on unexpected error")
        os._exit(1)

if __name__ == "__main__":
    main()
