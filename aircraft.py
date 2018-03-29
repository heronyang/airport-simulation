import enum
import logging

from clock import Clock
from config import Config
from utils import is_collinear


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
    Aircraft's location be set by the simulation.
    """
    def set_location(self, location):

        original_location = self.location
        self.location = location
        self.simulation.airport.update_aircraft_location(
            self, original_location, location)
        self.logger.info("%s changed location to %s" % (self, location))

    """
    Aircraft's true location while moving.
    """
    @property
    def true_location(self):

        if self.state is not State.moving:
            return self.location

        return self.pilot.itinerary.get_true_location(self.simulation.now)


    """
    Aircraft radio received new itinerary, and it will be passed to the pilot
    right the way.
    """
    def set_itinerary(self, itinerary):
        self.pilot.set_itinerary(itinerary)

    def tick(self):
        if self.state == State.moving:
            self.logger.info("%s at %s %s to %s" % (self, self.true_location,
                                                    self.state, self.location))
        else:
            self.logger.info("%s at %s %s" % (self, self.state, self.location))

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
            self.logger.error("%s: The itinerary is impossible to make it." %
                              self)
            return

        self.itinerary = itinerary
        self.logger.debug("%s: Roger, new itinerary %s received." %
                          (self, itinerary))

        for target in itinerary.targets:
            self.logger.debug(target)

    def tick(self):

        self.move()
        self.update_state()
        self.aircraft.tick()

    def move(self):

        if not self.itinerary:
            self.logger.debug("%s: No itinerary request." % self)
            return

        now = self.simulation.now
        while not self.itinerary.is_completed:
            next_target = self.itinerary.next_target

            # Pop one target node when 1) the top node is not the last one and
            # it's finished, or 2) the top node is the last one and we've
            # arrived the node
            if (next_target.edt is not None and next_target.edt <= now) or \
               (next_target.edt is None and next_target.eat <= now):
                past_target = self.itinerary.pop_target()

                # Move to the past node if it hasn't
                if not self.aircraft.location.is_close_to(past_target.node):
                    self.aircraft.set_location(past_target.node)
                    self.logger.debug("%s: Moved to %s." %
                                      (self, past_target))

                self.logger.debug("%s: %s finished." % (self, next_target))
                continue

            if not self.aircraft.location.is_close_to(next_target.node):
                self.aircraft.set_location(next_target.node)
                self.logger.debug("%s: Moved to %s." % (self, next_target))

            break

        if self.itinerary.is_completed:
            self.logger.debug("%s: %s completed." % (self, self.itinerary))
            self.itinerary = None

    def update_state(self):

        if not self.itinerary:
            self.aircraft.state = State.stop
            return

        now = self.simulation.now
        next_target = self.itinerary.next_target

        if now < next_target.eat:
            self.aircraft.state = State.moving
            return

        if now >= next_target.eat and now < next_target.edt:
            self.aircraft.state = State.hold
            return

        self.aircraft.state = State.uknown

    def is_heading_same(self, aircraft):
        if self.itinerary is None or aircraft.pilot.itinerary is None:
            return False
        if self.itinerary.next_target is None or\
           aircraft.pilot.itinerary.next_target is None:
            return False
        next_target = self.itinerary.next_target
        return is_collinear(next_target.node, self.aircraft.true_location,
                            aircraft.true_location)

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
