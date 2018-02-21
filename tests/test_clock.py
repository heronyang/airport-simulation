#!/usr/bin/env python

from clock import Clock
from config import Config

import sys
import unittest
sys.path.append('..')


class TestClock(unittest.TestCase):

    SIM_TIME = 300

    def test_init(self):

        clock = Clock()
        Config.params["simulation"]["time_unit"] = self.SIM_TIME

        self.assertEqual(clock.now.minute, 0)
        self.assertEqual(clock.now.hour, 0)

    def test_tick(self):

        clock = Clock()
        Config.params["simulation"]["time_unit"] = self.SIM_TIME

        clock.tick()
        self.assertEqual(clock.now.minute, self.SIM_TIME / 60)

        clock.tick()
        clock.tick()
        self.assertEqual(clock.now.minute, (self.SIM_TIME * 3) / 60)


if __name__ == '__main__':
    unittest.main()
