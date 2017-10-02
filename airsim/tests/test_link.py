#!/usr/bin/env python

import sys
import unittest
sys.path.append('..')

from node import Node
from link import Link

class TestLink(unittest.TestCase):

    n1 = Node("1", "node-1", { "lat": 51.5033640, "lng": -0.1276250 })
    n2 = Node("2", "node-2", { "lat": 51.5133640, "lng": -0.1276250 })
    n3 = Node("3", "node-3", { "lat": 51.5233640, "lng": -0.1286250 })
    nodes = [n1, n2, n3]

    def test_init(self):
        link = Link("123", "link-123", self.nodes)
        self.assertEqual(link.nodes, self.nodes)

    def test_get_length(self):
        link = Link("123", "link-123", self.nodes)
        self.assertAlmostEqual(link.get_length(), 7307.4965586731)

if __name__ == '__main__':
	unittest.main()
