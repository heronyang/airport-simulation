import sys
import unittest
sys.path.append('..')

from nodes import *

class TestKDFWNodes(unittest.TestCase):

    data_dir = "../data/KDFW/"

    def test_init(self):

        init(self.data_dir)

        # test sizes
        self.assertEqual(len(spot_map), 54)
        self.assertEqual(len(gate_map), 233)
        self.assertEqual(len(runway_map), 6)

        # test some samples
        self.assertEqual(spot_map["S110"], 215)
        self.assertEqual(spot_map["S5"], 0)
        self.assertEqual(gate_map["GTE"], 933)
        self.assertEqual(gate_map["B20"], 311)

        self.assertAlmostEqual(runway_map["17R"], -1.5751596499248826, 5)
        self.assertAlmostEqual(runway_map["13L"], -0.78539816339744828, 5)

if __name__ == '__main__':
	unittest.main()
