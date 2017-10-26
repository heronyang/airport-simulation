#!/usr/bin/env python3
import sys
import time
import logging
import argparse
import threading

from simulation import Simulation
from monitor import Monitor

is_finished = False

# Logger
log_format = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] "\
        "%(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_format,
                    datefmt="%H:%M:%S", stream=sys.stdout)
logger = logging.getLogger(__name__)

def main():

    # Parses arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--airport", help = "IATA airport code",
                        required = True)
    parser.add_argument('-g', "--graphic", help = "Enable graphical monitor",
                        action = "store_true", default=False)
    args = parser.parse_args()
    
    # Gets the arguments
    airport_code = args.airport
    is_monitor_enabled = args.graphic

    if is_monitor_enabled:
        start_with_monitor(airport_code)
    else:
        start(airport_code)

def start(airport_code):

    logger.debug("Starting the simulation")

    # Initializes the simulation
    simulation = Simulation(airport_code)

    try:
        while not is_finished:
            simulation.update()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.debug("Simulation exits")

def start_with_monitor(airport_code):

    logger.debug("Starting the simulation with monitor")

    global is_finished

    # Initializes the simulation
    simulation = Simulation(airport_code)

    # Initializes the monitor
    monitor = Monitor(simulation)

    # Runs simulation  (non-block)
    simulation_thread = threading.Thread(target = run_simulation_in_background,
                                         args = (simulation, monitor))
    simulation_thread.start()

    # Runs monitor (block)
    monitor.start()
    logger.debug("Monitor ends")

    is_finished = True

def run_simulation_in_background(simulation, monitor):

    global is_finished

    try:
        while not is_finished:
            simulation.update()
            monitor.update()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.debug("Background simulation done")

    self.logger.debug("Simulation ends")

if __name__ == "__main__":
    main()
