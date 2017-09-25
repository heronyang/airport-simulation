#!/usr/bin/env python

import sys
import unittest
sys.path.append('..')

from surface_manager import SurfaceManager

class TestSurfaceManager(unittest.TestCase):

    def test_init(self):
        surface_manager = SurfaceManager("sfo")
        self.assertEqual(len(surface_manager.surface.gates), 101)

if __name__ == '__main__':
	unittest.main()
