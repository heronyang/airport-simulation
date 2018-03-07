#!/usr/bin/env python

from node import Node

import sys
import unittest
sys.path.append('..')


class TestNode(unittest.TestCase):

    def test_init(self):

        name = "node-123"
        geo_pos = {"lat": 51.5033640, "lng": -0.1276250}
        node = Node(name, geo_pos)
        self.assertDictEqual(node.geo_pos, geo_pos)
        self.assertEqual(node.name, name)

    def test_invalid_geo_pos(self):

        name = "node-123"
        geo_pos = {"lat": 51.5033640, "lng": -0.1276250}
        self.assertRaises(Exception, Node(name, geo_pos))

    def test_compare_same(self):

        name = "node-123"
        geo_pos = {"lat": 51.5033640, "lng": -0.1276250}
        n1 = Node(name, geo_pos)
        n2 = Node(name, geo_pos)

        self.assertEqual(n1, n2)
        self.assertEqual(n1.__hash__(), n2.__hash__())
        self.assertTrue(n1.__eq__(n2))

    def test_compare_diff(self):

        name = "node-123"
        geo_pos_1 = {"lat": 51.5033640, "lng": -0.1276250}
        geo_pos_2 = {"lat": 51.1033640, "lng": -0.1276250}
        n1 = Node(name, geo_pos_1)
        n2 = Node(name, geo_pos_2)

        self.assertNotEqual(n1, n2)
        self.assertNotEqual(n1.__hash__(), n2.__hash__())
        self.assertFalse(n1.__eq__(n2))


if __name__ == '__main__':
    unittest.main()
