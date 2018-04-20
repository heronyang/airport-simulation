from schedule import Schedule
from config import Config
from aircraft import State
from scheduler.abstract_scheduler import AbstractScheduler


class Scheduler(AbstractScheduler):

    def schedule(self, simulation):

        self.logger.info("Scheduling start")
        itineraries = {}

        # Assigns route per aircraft without any separation constraint
        for aircraft in simulation.airport.aircrafts:

            itinerary = self.schedule_aircraft(aircraft, simulation)
            itineraries[aircraft] = itinerary

        # Resolves conflicts
        schedule = self.resolve_conflicts(itineraries, simulation)

        self.logger.info("Scheduling end")
        return schedule

    def resolve_conflicts(self, itineraries, simulation):

        # Gets configuration parameters
        (tick_times, max_attempt) = self.get_params()

        # Setups variables
        attempts = {}   # attemps[conflict] = count
        unsolvable_conflicts = set()

        while True:

            # Resets the itineraries (set their state to start node)
            self.reset_itineraries(itineraries)

            # Creates simulation copy for prediction
            predict_simulation = simulation.copy
            predict_simulation.airport.apply_schedule(
                Schedule(itineraries, 0, 0))

            for i in range(tick_times):

                # Gets conflict in current state
                conflict = self.get_conflict_to_solve(
                    predict_simulation.airport.next_conflicts,
                    unsolvable_conflicts
                )

                # If a conflict is found, tries to resolve it
                if conflict is not None:
                    try:
                        self.resolve_conflict(
                            simulation, itineraries, conflict, attempts,
                            unsolvable_conflicts, max_attempt)
                        # Okay, then re-run everything again
                        break
                    except ConflictException:
                        # The conflict isn't able to be solved, skip it in
                        # later runs
                        unsolvable_conflicts.add(conflict)
                        self.logger.warning("Gave up solving %s" % conflict)
                        # Re-run eveything again
                        break

                if i == tick_times - 1:
                    # Done, conflicts are all handled, return the schedule
                    self.reset_itineraries(itineraries)
                    return Schedule(
                        itineraries,
                        self.get_n_delay_added(attempts),
                        len(unsolvable_conflicts)
                    )

                # After dealing with the conflicts in current state, tick to
                # next state
                predict_simulation.quiet_tick()

    def resolve_conflict(self, simulation, itineraries, conflict, attempts,
                         unsolvable_conflicts, max_attempt):

        self.logger.info("Try to solve %s" % conflict)

        # Solves the first conflicts, then reruns everything again.
        aircraft = self.get_aircraft_to_delay(conflict, simulation)
        if aircraft in itineraries:

            # NOTE: New aircrafts that only appear in prediction are ignored
            aircraft.add_scheduler_delay()
            self.mark_attempt(attempts, max_attempt, conflict, aircraft,
                              itineraries)
            self.logger.info("Added delay on %s" % aircraft)

    def mark_attempt(self, attempts, max_attempt, conflict, aircraft,
                     itineraries):

        attempts[conflict] = attempts.get(conflict, 0) + 1
        if attempts[conflict] >= max_attempt:
            self.logger.error("Found deadlock")
            import pdb
            pdb.set_trace()
            # Reverse the delay
            itineraries[aircraft].restore()
            # Forget the attempts
            del attempts[conflict]
            raise ConflictException("Too many attempts")

    def get_params(self):

        rs_time = Config.params["simulation"]["reschedule_cycle"]
        sim_time = Config.params["simulation"]["time_unit"]
        tick_times = int(rs_time / sim_time) + 1
        max_attempt = \
            Config.params["scheduler"]["max_resolve_conflict_attempt"]

        return (tick_times, max_attempt)

    def get_conflict_to_solve(self, conflicts, unsolvable_conflicts):

        while True:
            if len(conflicts) == 0:
                return None
            if conflicts[0] in unsolvable_conflicts:
                conflicts = conflicts[1:]
            else:
                return conflicts[0]

    def get_aircraft_to_delay(self, conflict, simulation):

        a0, a1 = conflict.aircrafts

        if a0.state == State.moving and a1.state == State.hold:
            return a0
        if a0.state == State.hold and a1.state == State.moving:
            return a1
        if a0.state == State.hold and a1.state == State.hold:
            # This is the case generated by uncertainty in simulation and it's
            # unsolvable. However, if it's not generated by the uncertainty,
            # then this will be a bug needed to be fixed.
            self.logger.debug("Found conflict with two hold aircrafts")
            raise ConflictException("Unsolvable conflict found")

        return conflict.get_less_priority_aircraft(simulation.scenario)

    def get_n_delay_added(self, attempts):
        return sum(attempts.values())

    def reset_itineraries(self, itineraries):
        for _, itinerary in itineraries.items():
            itinerary.reset()


class ConflictException(Exception):
    pass
