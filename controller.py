"""
Ground Controller oversees the aircraft movement on the ground. It continuously observes the world and sends
commands to pilots when there is a notable situation.
"""


class Controller:
    def tick(self):
        # Call __observe.
        pass

    def __observe(self):
        """
        Observe the invertedAircraftLocations = {link: (aircraft, distance)} set.
        Observe the closestAircraft = {aircraft: (target_speed, distance)} dict.
        Observe potential conflicts.
        """
        pass

    def __resolve_conflicts(self):
        """
        If two aircraft on two links would enter the same link using their current speed, we see a potential conflict.
        Send command to one of the pilots to wait there.
        Will call Aircraft.Pilot.Slowdown() or something alike.
        """
        pass

    def find_closest_aircraft_ahead(self):
        pass
