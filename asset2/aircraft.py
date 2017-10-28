import enum
import logging

from clock import Clock
from config import Config

class State(enum.Enum):
    scheduled = 1   # Haven't appeared in the simulation
    moving = 2  # Moving on a route
    stopped = 3  # Stopped on a node

class Aircraft:
    """
    Aircraft contains information of a aircraft and states that the pilot
    knows. It won't obtain information other than its own state and operation.
    """

    def __init__(self, callsign, model, state, location):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        self.callsign = callsign
        self.model = model
        self.state = state
        self.location = location
        self.pilot = Pilot(self)

    """
    Aircraft location be set by the simulation.
    """
    def set_location(self, location):
        self.logger.debug("%s changed location to %s" % (self, location))
        self.location = location
        self.state = State.stopped

    """
    Aircraft radio received new itinerary, and it will be passed to the pilot
    right the way.
    """
    def add_itinerary(self, itinerary):
        self.pilot.add_itinerary(itinerary)

    @property
    def is_idle(self):
        return self.pilot.is_aircraft_idle

    """
    Moves forward based on the itinerary for `time` seconds. Returns the
    distance actually be moved.
    """
    def move(self, itinerary, velocity, time):
        distance = velocity * time
        self.location = itinerary.get_next_location(distance)
        self.state = State.moving
        self.logger.debug("Sets location to %s" % self.location)
        return distance

    """
    Stops the aircraft from moving.
    """
    def stop(self):
        self.state = State.stopped

    def operate(self, expected_v, delta_time):
        # TODO
        MAX_ACC = 0
        acc = max(MAX_ACC, (expected_v - self.v) / delta_time)
        # d = v * t + 0.5 * a * t^2
        distance = self.v * delta_time + 0.5 * acc * delta_time * delta_time
        self.v += acc * delta_time
        return distance

    def __hash__(self):
        return hash(self.callsign)

    def __eq__(self, other):
        return self.callsign == other.callsign

    def __ne__(self, other):
        return not(self == other)

    def __repr__(self):
        return "<Aircraft: %s>" % self.callsign

class Pilot:

    def __init__(self, aircraft):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        # TODO: velocity should be more dynamic based on current environment,
        # and acceleration
        self.expected_velocity = Config.PILOT_EXPECTED_VELOCITY

        self.aircraft = aircraft
        self.itineraries = []

    def add_itinerary(self, itinerary):
        self.itineraries.append(itinerary)
        self.logger.debug("Roger, new itinerary received.")

    """
    is_aircraft_idle returns true if there's no pending or ongoing itinerary
    and the aircraft is stopped.
    """
    @property
    def is_aircraft_idle(self):
        return len(self.itineraries) == 0 and \
                self.aircraft.state == State.stopped

    def tick(self):

        # If the aircraft is idle, do nothing on tick
        if self.is_aircraft_idle:
            self.logger.debug("No on-going itinerary request. Idle.")
            return

        # If the next itinerary expected start time is later than now, do
        # nothing
        iti = self.itineraries[0]
        if Clock.now < iti.expected_start_time:
            self.logger.debug("Itinerary request found but too early to start")
            return

        # Removes itinerary if we've arrived the end of the current itinerary
        if (iti.is_completed()):
            self.logger.debug("Itinerary %s completed" % iti)
            self.aircraft.stop()
            self.itineraries = self.itineraries[1:]
            return

        # Moves the aircraft then update the itinerary
        self.logger.debug("Moving %s according to %s for %s time units" %
                         (self.aircraft, iti, Clock.sim_time))
        distance = self.aircraft.move(iti, self.expected_velocity,
                                      Clock.sim_time)
        iti.update(distance)
