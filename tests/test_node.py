#!/usr/bin/env python

import sys
import unittest
sys.path.append('..')

from node import Node

class TestNode(unittest.TestCase):

    def test_init(self):

        index = "123"
        name = "node-123"
        geo_pos = { "lat": 51.5033640, "lng": -0.1276250 }
        node = Node(index, name, geo_pos)
        self.assertDictEqual(node.geo_pos, geo_pos)
        self.assertEqual(node.index, index)

    def test_invalid_geo_pos(self):
        index = "123"
        name = "node-123"
        geo_pos = { "lat": 51.5033640, "lng": -0.1276250 }
        self.assertRaises(Exception, Node(index, name, geo_pos))

if __name__ == '__main__':
	unittest.main()
