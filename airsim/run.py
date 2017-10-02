#!/usr/bin/env python3
import argparse

from simulation import Simulation
from monitor import Monitor

def main():

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

if __name__ == "__main__":

    main()
