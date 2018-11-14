"""`Aircraft` and `State` represents an aircraft in the simulation and its
state.
"""
import enum
import logging


class State(enum.Enum):
    """`State` is a enum object that represents a possible state of an aircraft.
    """
    unknown = 0
    stop = 1    # default for departure flights
    moving = 2
    hold = 3
    flying = 4  # default for arrival flights


class Aircraft:
    """`Aircraft` represents an aircraft in the airport.
    """

    def __init__(self, callsign, model, location, state):

        self.logger = logging.getLogger(__name__)

        self.callsign = callsign
        self.model = model
        self.location = location
        self.__state = state

        self.itinerary = None

    def set_location(self, location):
        """Sets the location of this aircraft to a given location."""

        self.location = location

        # print (self.logger)
        # if self.logger is None:
        #     self.logger = logging.getLogger(__name__)
        # self.logger.info("%s location changed to %s", self, location)

    @property
    def next_location(self):
        """Gets the location of this aircraft in the next tick."""
        if self.itinerary:
            next_target = self.itinerary.next_target
            if next_target is not None:
                return next_target
        return self.location

    def set_itinerary(self, itinerary):
        """Sets the itinerary of this aircraft."""
        self.itinerary = itinerary
        # self.logger.debug("%s: Roger, %s received.", self, itinerary)

        # for target in itinerary.targets:
        #     self.logger.debug(target)

    def add_uncertainty_delay(self):
        """Adds an uncertainty delay on this aircraft."""
        if not self.itinerary:
            # self.logger.debug("%s: No itinerary to add delay", self)
            return
        delay_added_at = self.itinerary.add_uncertainty_delay()
        # self.logger.debug("%s: Delay added at %s by uncertainty",
        #                   self, delay_added_at)

    def add_scheduler_delay(self):
        """Adds a scheduler delay on this aircraft."""
        if not self.itinerary:
            # self.logger.debug("%s: No itinerary to add delay", self)
            return
        delay_added_at = self.itinerary.add_scheduler_delay()
        # self.logger.debug("%s: Delay added at %s by scheduler",
        #                   self, delay_added_at)

    def tick(self):
        """Ticks on this aircraft and its subobjects to move to the next state.
        """

        if self.itinerary:
            self.itinerary.tick()
            if self.itinerary.is_completed:
                # self.logger.debug("%s: %s completed.", self, self.itinerary)
                pass
            else:
                self.set_location(self.itinerary.current_target)
        else:
            # self.logger.debug("%s: No itinerary request.", self)
            pass

        # self.logger.info("%s at %s", self, self.location)

    @property
    def state(self):
        """Returns the state of the current aircraft."""
        if self.itinerary is None or self.itinerary.is_completed:
            return State.stop
        if self.itinerary.next_target is None or\
           self.itinerary.current_target is None:
            return State.stop
        return State.hold if self.itinerary.current_target.is_close_to(
            self.itinerary.next_target) else State.moving

    @property
    def is_delayed(self):
        """Returns True if the aircraft is currently be delayed."""
        return self.itinerary.is_delayed if self.itinerary else False

    def set_quiet(self, logger):
        """Sets the aircraft into quiet mode where less logs are printed."""
        self.logger = logger

    def __hash__(self):
        return hash(self.callsign)

    def __eq__(self, other):
        return self.callsign == other.callsign

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "<Aircraft: %s %s>" % (self.callsign, self.state)

    def __getstate__(self):
        attrs = dict(self.__dict__)
        del attrs["logger"]
        return attrs

    def __setstate__(self, attrs):
        self.__dict__.update(attrs)
