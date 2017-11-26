import enum
import logging

from clock import Clock
from config import Config

class State(enum.Enum):
    init = 0        # the aircraft had never received any itinerary request yet
    idle = 1        # all itineraries had been completed
    scheduled = 2   # the itinerary is scheduled but it's not started
    moving = 3      # the aircraft is moving to the next target node
    pending = 4     # the aircraft just  one target node (may not be the
                    # final destination)

class Aircraft:
    """
    Aircraft contains information of a aircraft and states that the pilot
    knows. It won't obtain information other than its own state and operation.
    """

    def __init__(self, callsign, model, location):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        self.callsign = callsign
        self.model = model
        self.location = location
        self.pilot = Pilot(self)

    """
    Aircraft location be set by the simulation.
    """
    def set_location(self, location):

        self.logger.debug("%s changed location to %s" % (self, location))
        self.location = location

    """
    Aircraft radio received new itinerary, and it will be passed to the pilot
    right the way.
    """
    def set_itinerary(self, itinerary):
        self.pilot.set_itinerary(itinerary)

    @property
    def is_idle(self):
        return self.pilot.is_aircraft_idle

    def __hash__(self):
        return hash(self.callsign)

    def __eq__(self, other):
        return self.callsign == other.callsign

    def __ne__(self, other):
        return not(self == other)

    def __repr__(self):
        return "<Aircraft: %s>" % self.callsign

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)

    def set_quiet(self, logger):
        self.logger = logger
        self.pilot.set_quiet(logger)

class Pilot:

    def __init__(self, aircraft):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        self.aircraft = aircraft
        self.itinerary = None

    def set_itinerary(self, itinerary):

        self.itinerary = itinerary
        self.logger.debug("%s: Roger, new itinerary %s received." %
                          (self, itinerary))

    """
    is_aircraft_idle returns true if there's no pending or ongoing itinerary
    and the aircraft is stopped.
    """
    @property
    def is_aircraft_idle(self):
        return self.itinerary is None or self.itinerary.is_completed

    def tick(self, uc, flight):

        state = self.state

        self.logger.debug("Aircraft (%s) location: %s, state: %s" %
                         (self.aircraft, self.aircraft.location, self.state))

        # If the aircraft is idle, do nothing on tick
        if state == State.init or state == State.idle:
            self.logger.debug("%s: No on-going itinerary request." % self)
            return

        # If the itinerary shouldn't be started yet, do nothing
        if state == State.scheduled:
            self.logger.debug("%s: It's too early to start %s." %
                              (self, self.itinerary))
            return

        # Pulls out the next target node
        if state == State.moving:
            next_target_node = self.itinerary.peek_target_node()
            self.logger.debug("%s: I'm on my way to next node %s.",
                              self, next_target_node)
            return

        # Moves one or more nodes until there's no pending node to arrive or
        # the next node is still too early to arrive.
        while True:
            if not uc:
                self.move_aircraft_to_next_target_node()
            else: # has uc
                near_terminal=self.aircraft.location.is_close_to(flight.from_gate)
                if uc.aircraft_can_move(near_terminal):
                    self.move_aircraft_to_next_target_node()

            if self.state is State.moving or \
               self.state is State.idle:
                break

    def move_aircraft_to_next_target_node(self):

        next_target_node = self.itinerary.peek_target_node()

        # Arrives the aircraft on the target node
        self.aircraft.set_location(next_target_node.node)
        self.itinerary.pop_target_node()
        self.logger.debug("%s: Arrived target node %s at time %s" %
                          (self, next_target_node, Clock.now))

    @property
    def state(self):

        if self.itinerary is None:
            return State.init

        if self.itinerary.is_completed:
            return State.idle

        if not self.itinerary.is_started:
            return State.scheduled

        next_target_node = self.itinerary.peek_target_node()
        if Clock.now < next_target_node.expected_arrival_time:
            return State.moving

        return State.pending

    def __repr__(self):
        return "<Pilot on %s>" % self.aircraft

    def __getstate__(self):
        d = dict(self.__dict__)
        del d["logger"]
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)

    def set_quiet(self, logger):
        self.logger = logger
