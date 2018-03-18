import logging

from schedule import Schedule
from aircraft import Aircraft, State
from route import Route
from itinerary import Itinerary
from config import Config
from utils import get_seconds_after, get_seconds, get_seconds_taken
from heapdict import heapdict
from scheduler.abstract_scheduler import AbstractScheduler


class Scheduler(AbstractScheduler):

    def schedule(self, simulation):

        self.logger.info("Scheduling start")
        last_occupied_time = {}

        # Sorts the flights by its departure or arrival time (prioirty queue)
        h = heapdict()
        for aircraft in simulation.airport.aircrafts:

            # TODO: moving aircrafts should retrieve a new itinerary at the
            # next node
            if aircraft.state is not State.stop:
                continue

            # TODO: adds for arrivals
            flight = simulation.scenario.get_flight(aircraft)
            h[aircraft] = flight.departure_time

        itineraries = {}
        while len(h) is not 0:
            aircraft, _ = h.popitem()
            itinerary = self.schedule_aircraft(aircraft, simulation,
                                               last_occupied_time)
            itineraries[aircraft] = itinerary

        self.logger.info("Scheduling end")
        return Schedule(itineraries)
