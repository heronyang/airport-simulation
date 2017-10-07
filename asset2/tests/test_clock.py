#!/usr/bin/env python

import sys
import unittest
sys.path.append('..')

from clock import Clock

class TestClock(unittest.TestCase):

    def test_init(self):
        clock = Clock()
        self.assertEqual(clock.now().minute, 0)

    def test_tick(self):
        clock = Clock()
        clock.tick()
        self.assertEqual(clock.now().minute, 15)
        clock.tick()
        clock.tick()
        self.assertEqual(clock.now().minute, 45)

if __name__ == '__main__':
	unittest.main()
