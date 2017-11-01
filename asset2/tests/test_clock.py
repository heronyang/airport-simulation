#!/usr/bin/env python

import sys
import unittest
sys.path.append('..')

from clock import Clock

class TestClock(unittest.TestCase):

    SIM_TIME = 300

    def test_init(self):
        clock = Clock()
        Clock.sim_time = self.SIM_TIME
        self.assertEqual(clock.now.minute, 0)

    def test_tick(self):
        clock = Clock()
        Clock.sim_time = self.SIM_TIME
        clock.tick()
        self.assertEqual(clock.now.minute, self.SIM_TIME / 60)
        clock.tick()
        clock.tick()
        self.assertEqual(clock.now.minute, (self.SIM_TIME * 3)/ 60)

if __name__ == '__main__':
	unittest.main()
