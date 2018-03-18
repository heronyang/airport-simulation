import logging

from schedule import Schedule
from config import Config
from scheduler.abstract_scheduler import AbstractScheduler


class Scheduler(AbstractScheduler):

    def schedule(self, simulation):

        self.logger.info("Scheduling start")
        itineraries = {}

        # Assigns route per aircraft without any separation constraint
        for aircraft in simulation.airport.aircrafts:

            itinerary = self.schedule_aircraft(aircraft, simulation)
            itineraries[aircraft] = itinerary

        # Resolve conflicts
        self.resolve_conflicts(itineraries, simulation)

        self.logger.info("Scheduling end")
        return Schedule(itineraries)

    def resolve_conflicts(self, itineraries, simulation):

        sim_time = Config.params["simulation"]["time_unit"]
        rc_time = Config.params["scheduler"]["resolve_conflicts_time"]
        delay_time = Config.params["scheduler"]["delay_time"]

        while True:

            for time_from_now in range(sim_time, rc_time, sim_time):

                schedule = Schedule(itineraries)
                predict_state = simulation.predict_state_after(
                    schedule, time_from_now)

                conflicts = predict_state.airport.conflicts

                if len(conflicts) == 0:
                    break

                # Solves the first conflicts, then rerun everything again
                conflict = conflicts[0]

                # TODO
                aircraft = conflict.get_less_priority_aircraft(
                    simulation.scenario)
                itineraries[aircraft].add_delay(delay_time)
