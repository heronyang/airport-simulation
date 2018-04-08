import enum
import logging


class State(enum.Enum):

    unknown = 0
    stop = 1    # default for departure flights
    moving = 2
    hold = 3
    flying = 4  # default for arrival flights


class Aircraft:

    def __init__(self, callsign, model, location, state):

        self.logger = logging.getLogger(__name__)

        self.callsign = callsign
        self.model = model
        self.location = location
        self.__state = state

        self.itinerary = None

    def set_location(self, location):

        original_location = self.location
        self.location = location
        self.logger.info("%s location changed to %s" % (self, location))

    @property
    def next_location(self):
        if self.itinerary:
            nl = self.itinerary.next_target
            if nl is not None:
                return nl
        return self.location

    def set_itinerary(self, itinerary):

        self.itinerary = itinerary
        self.logger.debug("%s: Roger, %s received." % (self, itinerary))

        for target in itinerary.targets:
            self.logger.debug(target)

    def add_delay(self):
        if not self.itinerary:
            self.logger.debug("%s: No itinerary to add delay", self)
            return
        delay_added_at = self.itinerary.add_delay()
        self.logger.debug("%s: Delay added at %s" % (self, delay_added_at))

    def tick(self):

        if self.itinerary:
            self.itinerary.tick()
            if self.itinerary.is_completed:
                self.logger.debug("%s: %s completed." % (self, self.itinerary))
                self.itinerary = None
            else:
                self.set_location(self.itinerary.current_target)
        else:
            self.logger.debug("%s: No itinerary request." % self)

        self.logger.info("%s at %s" % (self, self.location))

    @property
    def state(self):
        if not self.itinerary or self.itinerary.is_completed:
            return State.stop
        return State.hold if self.itinerary.current_target.is_close_to(
                    self.itinerary.next_target) else State.moving

    @property
    def is_delayed(self):
        return self.itinerary.is_delayed if self.itinerary else False

    def set_quiet(self, logger):
        self.logger = logger

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
