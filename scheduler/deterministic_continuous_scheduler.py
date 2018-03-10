import logging

from schedule import Schedule
from aircraft import Aircraft, State
from route import Route
from itinerary import Itinerary
from config import Config
from utils import get_seconds_after, get_seconds, get_seconds_taken
from heapdict import heapdict
from scheduler.abstract_scheduler import AbstractScheduler


class Scheduler(AbstractScheduler):
    # TODO
    pass
