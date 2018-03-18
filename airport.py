import os
import logging
import itertools

from surface import SurfaceFactory
from config import Config
from conflict import Conflict
from aircraft import State
from node import get_middle_node
from copy import deepcopy


class Airport:
    """
    Airport contains the surface and all the aircrafts currently moving or
    stopped in this airport.
    """

    def __init__(self, simulation, code, surface):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        # Runtime data
        self.aircrafts = []

        # Pointer to the simulation
        self.simulation = simulation

        # Queues for departure flights at gates
        self.gate_queue = {}

        # Inverse lookup from node to aircraft
        self.node2aircraft = {}

        # Static data
        self.code = code
        self.surface = surface

    def apply_schedule(self, schedule):
        # NOTE: the aircraft in schedule may be different from the one in
        # the airport, they should be retrieved by comparing the callsign
        # (hash)
        for aircraft, itinerary in schedule.itineraries.items():
            is_applied = False
            for airport_aircraft in self.aircrafts:
                if airport_aircraft == aircraft:
                    airport_aircraft.set_itinerary(deepcopy(itinerary))
                    is_applied = True
                    break
            if not is_applied:
                raise Exception("%s not found in the airport" % r.aircraft)


    def update_aircraft_location(self, aircraft, original_location, location):
        self.logger.info("Update %s location from %s to %s" % 
                        (aircraft, original_location, location))

        # Removes previous one if found
        if original_location in self.node2aircraft:
            self.node2aircraft[original_location].remove(aircraft)

        # Appends the new one
        s = self.node2aircraft.get( location, set())
        s.add(aircraft)
        self.node2aircraft[location] = s

    def is_occupied_at(self, node):
        return node in self.node2aircraft and len(self.node2aircraft[node]) > 0

    def add_aircraft(self, aircraft):
        self.aircrafts.append(aircraft)

    def remove_aircraft(self, aircraft):
        self.aircrafts.remove(aircraft)

    @property
    def conflicts_at_node(self):

        occupied_by = {}
        for aircraft in self.aircrafts:
            if aircraft.state == State.moving:
                continue
            location = aircraft.location
            entry = occupied_by.get(location, [])
            entry.append(aircraft)
            occupied_by[location] = entry

        now = self.simulation.now
        result = []
        for location in occupied_by:
            aircrafts = occupied_by[location]
            if len(aircrafts) <= 1:
                continue
            result.append(Conflict(location, aircrafts, now))
        return result

    @property
    def conflicts(self):

        cs = []

        separation = Config.params["simulation"]["separation"]
        aircraft_pairs = list(itertools.combinations(self.aircrafts, 2))
        for ap in aircraft_pairs:
            l0, l1 = ap[0].true_location, ap[1].true_location
            if l0.get_distance_to(l1) > separation:
                continue
            middle_node = get_middle_node(l0, l1)
            cs.append(Conflict(middle_node, ap, self.simulation.now))

        return cs

    def tick(self):
        for aircraft in self.aircrafts:
            aircraft.pilot.tick()

    def print_stats(self):
        self.surface.print_stats()

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)

    def set_quiet(self, logger):
        self.logger = logger
        self.surface.set_quiet(logger)


class AirportFactory:

    @classmethod
    def create(self, simulation, code):

        dir_path = Config.DATA_ROOT_DIR_PATH % code

        # Checks if the folder exists
        if not os.path.exists(dir_path):
            raise Exception("Surface data is missing")

        surface = SurfaceFactory.create(dir_path)
        return Airport(simulation, code, surface)
