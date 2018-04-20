#!/usr/bin/env python

from node import Node
from link import Link
from config import Config

import sys
import unittest
sys.path.append('..')


class TestLink(unittest.TestCase):

    n1 = Node("node-1", {"lat": 51.5033640, "lng": -0.1276250})
    n2 = Node("node-2", {"lat": 51.5133640, "lng": -0.1276250})
    n3 = Node("node-3", {"lat": 51.5233640, "lng": -0.1286250})
    nodes = [n1, n2, n3]

    # link_node1 and link_node2 locates near the link between n1 and n2;
    # link_node3 is far from the link between n1 and n2
    link_node1 = Node("ln-1", {"lat": 51.50654, "lng": -0.12765})
    link_node2 = Node("ln-2", {"lat": 51.50648, "lng": -0.12781})
    link_node3 = Node("ln-3", {"lat": 51.50647, "lng": -0.12845})

    def test_init(self):
        link = Link("link-123", self.nodes)
        self.assertEqual(link.nodes, self.nodes)

    def test_length(self):
        link = Link("link-123", self.nodes)
        self.assertAlmostEqual(link.length, 7307.4965586731)

    def test_contains_node(self):
        link = Link("link-123", self.nodes)
        Config.params["simulation"]["close_node_link_threshold"] = 10
        self.assertTrue(link.contains_node(self.link_node1))
        self.assertTrue(link.contains_node(self.link_node2))
        self.assertFalse(link.contains_node(self.link_node3))
        self.assertFalse(link.contains_node(self.n1))

    def test_break_at_normal(self):

        link = Link("link-123", self.nodes)
        Config.params["simulation"]["close_node_link_threshold"] = 10
        links = link.break_at(self.link_node1)
        self.assertEqual(len(links), 2)
        self.assertAlmostEqual(links[0].length + links[1].length,
                               link.length, 1)

    def test_break_at_end_node(self):

        link = Link("link-123", self.nodes)
        Config.params["simulation"]["close_node_link_threshold"] = 10
        self.assertRaises(Exception, link.break_at, self.n1)

    def test_break_at_end_node_near(self):

        link = Link("link-123", self.nodes)
        Config.params["simulation"]["close_node_link_threshold"] = 10
        self.assertRaises(Exception, link.break_at, self.link_node3)


if __name__ == '__main__':
    unittest.main()
