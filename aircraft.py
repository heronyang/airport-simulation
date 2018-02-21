import enum
import logging

from clock import Clock
from config import Config


class State(enum.Enum):

    unknown = 0
    stop = 1    # default for departure flights
    moving = 2
    hold = 3
    flying = 4  # default for arrival flights


class Aircraft:

    """
    Aircraft contains information of a aircraft and states that the pilot
    knows. It won't obtain information other than its own state and operation.
    """

    def __init__(self, simulation, callsign, model, location, state):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        self.simulation = simulation
        self.callsign = callsign
        self.model = model
        self.location = location
        self.pilot = Pilot(simulation, self)
        self.state = state

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

    def tick(self):
        self.logger.info("%s at %s %s" %
                         (self, self.location, self.state))

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

    def __init__(self, simulation, aircraft):

        # Setups the logger
        self.logger = logging.getLogger(__name__)

        self.simulation = simulation
        self.aircraft = aircraft
        self.itinerary = None

    def set_itinerary(self, itinerary):

        if not itinerary.is_valid(self.simulation.clock.now):
            self.logger.debug("%s: The itinerary is impossible to make it." %
                              self)
            return

        self.itinerary = itinerary
        self.logger.debug("%s: Roger, new itinerary %s received." %
                          (self, itinerary))

    def tick(self):

        self.move()
        self.update_state()
        self.aircraft.tick()

    def move(self):

        if not self.itinerary:
            self.logger.debug("%s: No itinerary request." % self)
            return

        now = self.simulation.clock.now
        while not self.itinerary.is_completed:
            next_node = self.itinerary.next_node

            # Pop one target node when 1) the top node is not the last one and
            # it's finished, or 2) the top node is the last one and we've
            # arrived the node
            if (next_node.edt is not None and next_node.edt <= now) or \
               (next_node.edt is None and next_node.eat <= now):
                self.itinerary.pop_node()
                self.logger.debug("%s: %s finished." % (self, next_node))
                continue

            if not self.aircraft.location.is_close_to(next_node.node):
                self.aircraft.set_location(next_node.node)
                self.logger.debug("%s: Moved to %s." % (self, next_node))

            break

        if self.itinerary.is_completed:
            self.itinerary = None
            self.logger.debug("%s: %s completed." % (self, self.itinerary))

    def update_state(self):

        if not self.itinerary:
            self.aircraft.state = State.stop
            return

        now = self.simulation.clock.now
        next_node = self.itinerary.next_node

        if now < next_node.eat:
            self.aircraft.state = State.moving
            return

        if now >= next_node.eat and now < next_node.edt:
            self.aircraft.state = State.hold
            return

        self.aircraft.state = State.uknown

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
