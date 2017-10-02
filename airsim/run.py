#!/usr/bin/env python3
import sys
import time
import argparse
import threading

from simulation import Simulation
from monitor import Monitor

is_finished = False

def main():

    global is_finished

    # Parses arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--airport", help = "IATA airport code",
                        required = True)
    args = parser.parse_args()
    airport_code = args.airport

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
    print("Monitor ends")

    is_finished = True

def run_simulation_in_background(simulation, monitor):
    global is_finished
    try:
        while not is_finished:
            print("Updating...")
            simulation.update()
            monitor.update()
            time.sleep(1)
            simulation.get_airport().gates = []
            time.sleep(1)
    except KeyboardInterrupt:
        print("Background simulation done")

    print("Simulation ends")

if __name__ == "__main__":
    main()
