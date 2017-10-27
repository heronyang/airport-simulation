#!/usr/bin/env python3
import sys
import time
import logging
import argparse
import threading
import traceback

from simulation import Simulation
from monitor import Monitor
from clock import ClockException

DEFAULT_TICK_PAUSE_TIME = 1
DEFAULT_TICK_SIM_TIME = 5 * 60
DEFAULT_SCHEDULE_SIM_TIME = 15 * 60

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
                        default = DEFAULT_TICK_PAUSE_TIME)
    parser.add_argument("-t", "--tick-sim-time", type = int,
                        help = "Seconds past between each tick in the " \
                        "simluated world", default = DEFAULT_TICK_SIM_TIME)
    parser.add_argument("-ts", "--schedule-sim-time", type = int,
                       help = "Seconds past between scheduling requests in" \
                        "simulated world (seconds)",
                        default = DEFAULT_SCHEDULE_SIM_TIME)

    return parser.parse_args()

def start(params):

    logger.debug("Starting the simulation")

    # Initializes the simulation
    simulation = Simulation(params.airport,
                            params.tick_sim_time,
                            params.schedule_sim_time)

    # Starts to tick periodically
    try:
        while not is_finished:
            simulation.tick()
            time.sleep(params.tick_pause_time)
    except KeyboardInterrupt:
        logger.debug("Caught keyboard interrupt, simulation exits")
    except ClockException:
        logger.debug("Simulation ends")
        # TODO: Should ask the simulation for performance result here
    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.debug("Simulation exists on unexpected error")

def start_with_monitor(params):

    logger.debug("Starting the simulation with monitor")

    global is_finished

    # Initializes the simulation
    simulation = Simulation(params.airport,
                            params.tick_sim_time,
                            params.schedule_sim_time)

    # Initializes the monitor
    monitor = Monitor(simulation)

    # Runs simulation  (non-block)
    simulation_thread = threading.Thread(
        target = run_simulation_in_background,
        args = (simulation, monitor, params.tick_pause_time))
    simulation_thread.start()

    # Runs monitor (block)
    monitor.start()
    logger.debug("Monitor ends")

    is_finished = True

def run_simulation_in_background(simulation, monitor, pause_time):

    global is_finished

    try:
        while not is_finished:
            simulation.tick()
            monitor.tick()
            time.sleep(pause_time)
    except KeyboardInterrupt:
        logger.debug("Background simulation done")
    except Exception:
        logger.debug("Simulation exists")

    logger.debug("Simulation ends")

if __name__ == "__main__":
    main()
