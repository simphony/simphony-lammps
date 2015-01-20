import unittest

from simlammps.config.pair_style import PairStyle

from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer


class TestPairStyle(unittest.TestCase):
    """ Tests the pair style config class

    """
    def test_lj_cut(self):
        CM = DataContainer()
        CM[CUBA.PAIR_STYLE] = ("lj:\n"
                               "  global_cutoff: 1.12246\n"
                               "  parameters:\n"
                               "  - pair: [1, 1]\n"
                               "    epsilon: 1.0\n"
                               "    sigma: 1.0\n"
                               "    cutoff: 1.2246\n"
                               "  - pair: [1, 2]\n"
                               "    epsilon: 1.0\n"
                               "    sigma: 1.0\n"
                               "    cutoff: 1.2246\n"
                               "  - pair: [1, 3]\n"
                               "    epsilon: 1.0\n"
                               "    sigma: 1.0\n"
                               "    cutoff: 1.2246\n"
                               "  - pair: [2, 2]\n"
                               "    epsilon: 1.0\n"
                               "    sigma: 1.0\n"
                               "    cutoff: 1.2246\n"
                               "  - pair: [2, 3]\n"
                               "    epsilon: 1.0\n"
                               "    sigma: 1.0\n"
                               "    cutoff: 1.2246\n"
                               "  - pair: [3, 3]\n"
                               "    epsilon: 1.0\n"
                               "    sigma: 1.0\n"
                               "    cutoff: 1.0001\n")

        pair_style = PairStyle(CM)
        self.assertEqual(
            pair_style.get_global_config(), "pair_style lj/cut 1.12246")

        lines = pair_style.get_pair_coeffs().split("\n")
        self.assertTrue("pair_coeff 1 1 1.0 1.0 1.2246" in lines)
        self.assertTrue("pair_coeff 1 2 1.0 1.0 1.2246" in lines)
        self.assertTrue("pair_coeff 1 3 1.0 1.0 1.2246" in lines)
        self.assertTrue("pair_coeff 2 2 1.0 1.0 1.2246" in lines)
        self.assertTrue("pair_coeff 2 3 1.0 1.0 1.2246" in lines)
        self.assertTrue("pair_coeff 3 3 1.0 1.0 1.0001" in lines)

if __name__ == '__main__':
    unittest.main()
