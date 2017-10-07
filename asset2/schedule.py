class ScheduleFactory:

    @classmethod
    def create(self, dir_path):
        return Schedule()

class Schedule:
    """
    Schedule contains a list of arrival flights and a list of depature flights.
    The flight information is designed for read-only and shall only be updated
    when we decided to change delay some certain flights. It's like the
    schedule we see on the screens in the airports.
    """

    arrivals = []
    departures = []

    pass
