import sys
import unittest
from unittest.mock import MagicMock
from scheduler import SchedulerFactory, FCFSScheduler

sys.path.append('..')

class TestScheduler(unittest.TestCase):

	def side_effect(self, *args):
		vals = { 
			('A',): [0, 4, 6], 
			('B',): [0, 4, 8, 9], 
			('C',): [1, 2, 3, 4, 5], 
			('D',): [1, 2, 6, 7, 8, 9]
				}

		return vals[args]

	def setUp(self):
		requests = [('a1', 'A', 4),
		('a2', 'B', 5),
		('a3', 'C', 6),
		('a4', 'D', 8),
		('a5', 'A', 8),
		('a6', 'D', 10),
		('a7', 'C', 10),
		('a8', 'D', 15),
		('a9', 'A', 15),
		('a10', 'C', 16),
		('a11', 'A', 16)]

		self.sch = SchedulerFactory.create(requests, debug = True)
		self.sch.getRoute = MagicMock(side_effect=self.side_effect)

	def test_FCFS_basic(self):
		out = self.sch.generateSchedule()
		expected = [
		('a1', [(0, 4), (4, 5), (6, 6)]), 
		('a2', [(0, 5), (4, 6), (8, 7), (9, 8)]), 
		('a3', [(1, 6), (2, 7), (3, 8), (4, 9), (5, 10)]), 
		('a4', [(1, 8), (2, 9), (6, 10), (7, 11), (8, 12), (9, 13)]), 
		('a5', [(0, 9), (4, 10), (6, 11)]), 
		('a6', [(1, 10), (2, 11), (6, 12), (7, 13), (8, 14), (9, 15)]), 
		('a7', [(1, 11), (2, 12), (3, 13), (4, 14), (5, 15)]), 
		('a8', [(1, 15), (2, 16), (6, 17), (7, 18), (8, 19), (9, 20)]), 
		('a9', [(0, 16), (4, 17), (6, 18)]), 
		('a10', [(1, 16), (2, 17), (3, 18), (4, 19), (5, 20)]), 
		('a11', [(0, 17), (4, 18), (6, 19)])]
		self.assertEqual(out, expected)
