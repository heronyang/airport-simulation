#!/usr/bin/env python3
"""
Scenario generating script is sepearated from the surface data since it's
currently handcrafted. Unlike `generate.py`, this script is not generally
working with any kind of data but specifying on the `Simple Data` we created.
"""

import sys
import random
import logging
import numpy

from utils import export_to_json, create_output_folder

OUTPUT_FOLDER = "./build/"

TIGHTNESS_TIME_MEAN = 180  # seconds
TIGHTNESS_TIME_DEVIATION = 30  # seconds
APPEAR_BEFORE = 0  # seconds

# We stop adding flights before the day ends in order to measure maxspan
END_TIME = 9 * 60 * 60  # seconds

# Setups logger
logger = logging.getLogger(__name__)
logger_handler = logging.StreamHandler(sys.stdout)
logger_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger_handler.setLevel(logging.DEBUG)
logger.addHandler(logger_handler)
logger.setLevel(logging.DEBUG)

flight_template = {
    "model": "A319",
    "airport": "SJC",
    "runway": "10R/28L",
}

gates = ["50", "55", "53", "52", "54A", "51A", "51B", "54B", "56B", "56A",
         "57", "59", "58B", "58A"]

spots = ["S2", "S3"]


def main():
    """
    Scenario is generated based on random flight arrangements. Flights are
    appeared every `interval` seconds where `interval` is random variable given
    a predefined mean and deviation.
    """

    # Creates the output folder
    create_output_folder(OUTPUT_FOLDER)
    current_time = 0

    # In this scenario, we only have departure flights to simply the problem
    departures = []
    while current_time < END_TIME:
        flight = generate_flight_at(current_time)
        departures.append(flight)
        interval = get_random_time_interval()
        current_time += interval

    scenario = {"arrivals": [], "departures": departures}

    # Saves to file
    output_filename = OUTPUT_FOLDER + "scenario.json"
    export_to_json(output_filename, scenario)

    logger.debug("Done")


index = 1


def generate_flight_at(time):
    global index
    flight = flight_template.copy()

    flight["callsign"] = "F" + str(index)
    flight["time"] = sec2time_str(time)
    flight["appear_time"] = sec2time_str(time - APPEAR_BEFORE)
    flight["gate"] = random.choice(gates)

    # NOTE: spot position is not actually be used in our simulation, so we pick
    # it randomly
    flight["spot"] = random.choice(spots)

    index += 1
    return flight


def sec2time_str(time):
    if time < 0:
        return "0000"
    if time > 24 * 60 * 60:
        return "2359"
    minute = (time / 60) % 60
    hour = (time / 60) / 60
    return "%02d%02d" % (hour, minute)


def get_random_time_interval():
    while True:
        interval = numpy.random.normal(TIGHTNESS_TIME_MEAN,
                                       TIGHTNESS_TIME_DEVIATION)
        if interval > 0:
            return interval


if __name__ == "__main__":
    main()
