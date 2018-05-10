"""Class file for `Schedule`."""


class Schedule:
    """`Schedule` contains itineraries for each aircraft."""

    def __init__(self, itineraries, n_delay_added, n_unsolvable_conflicts):
        self.itineraries = itineraries
        self.n_delay_added = n_delay_added
        self.n_unsolvable_conflicts = n_unsolvable_conflicts
