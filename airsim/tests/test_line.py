#!/usr/bin/env python

import sys
import unittest
sys.path.append('..')

from node import Node
from line import Line

class TestLine(unittest.TestCase):

    n1 = Node("node-1", { "lat": 51.5033640, "lng": -0.1276250 })
    n2 = Node("node-2", { "lat": 51.5133640, "lng": -0.1276250 })
    n3 = Node("node-3", { "lat": 51.5233640, "lng": -0.1286250 })
    nodes = [n1, n2, n3]

    def test_init(self):
        line = Line("line-123", self.nodes)
        self.assertEqual(line.get_nodes(), self.nodes)

    def test_get_length(self):
        line = Line("line-123", self.nodes)
        self.assertAlmostEqual(line.get_length(), 7307.4965586731)

if __name__ == '__main__':
	unittest.main()
