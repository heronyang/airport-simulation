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
        schedule = self.resolve_conflicts(itineraries, simulation)

        self.logger.info("Scheduling end")
        return schedule

    def resolve_conflicts(self, itineraries, simulation):

        rc_time = Config.params["scheduler"]["resolve_conflicts_time"]
        sim_time = Config.params["simulation"]["time_unit"]
        delay_time = Config.params["scheduler"]["delay_time"]

        successful_tick_times = int(rc_time / sim_time)
        n_delay_added = 0

        while True:

            predict_simulation = simulation.copy
            predict_simulation.airport.apply_schedule(Schedule(itineraries, 0))

            # Finishes currenct tick
            predict_simulation.remove_aircrafts()
            predict_simulation.clock.tick()

            for i in range(successful_tick_times):

                predict_simulation.quiet_tick()
                conflicts = predict_simulation.airport.conflicts

                if len(conflicts) == 0:
                    # If it's the last check, return
                    if i == successful_tick_times - 1:
                        return Schedule(itineraries, n_delay_added)
                    continue

                self.logger.info("Found %s" % conflicts[0])
                
                # Solves the first conflicts, then reruns everything again.
                aircraft = self.get_aircraft_to_delay(conflicts, simulation)
                if aircraft in itineraries:
                    # New aircrafts that only appear in prediction are ignored
                    itineraries[aircraft].add_delay(delay_time)
                    n_delay_added += 1
                    self.logger.info("Added %d delay on %s" %
                                     (delay_time, aircraft))
                break

    def get_aircraft_to_delay(self, conflicts, simulation):
        # Solves the first conflicts, then reruns everything again. They way we
        # solve a conflict is to add delay on the aircraft the is closer to the
        # target node if they are currently standing on the same line;
        # otherwise, we pick the one with less priority to delay.
        conflict = conflicts[0]
        a0, a1 = conflict.aircrafts
        if a0.pilot.is_heading_same(a1):
            next_target = a0.pilot.itinerary.next_target
            d0 = a0.true_location.get_distance_to(next_target.node)
            d1 = a1.true_location.get_distance_to(next_target.node)
            return a0 if d0 < d1 else a1
        return conflict.get_less_priority_aircraft(simulation.scenario)
