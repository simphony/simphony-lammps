import unittest

from numpy.testing import assert_almost_equal

from simlammps.config.domain import get_box
from simlammps.cuba_extension import CUBAExtension


class TestDomain(unittest.TestCase):
    """ Tests the domain config class

    """
    def test_missing_domain(self):
        with self.assertRaises(RuntimeError):
            get_box([])

        with self.assertRaises(RuntimeError):
            get_box([{}, {}])

    def test_non_matching_domains(self):
        vectors1 = [(25.0, 0.0, 0.0),
                    (0.0, 22.0, 0.0),
                    (0.0, 0.0, 1.0)]

        with self.assertRaises(RuntimeError):
            get_box([{CUBAExtension.BOX_VECTORS: vectors1}, {}])

        vectors2 = [(2.0, 0.0, 0.0),
                    (0.0, 1.0, 0.0),
                    (0.0, 0.0, 1.0)]

        with self.assertRaises(RuntimeError):
            get_box([{CUBAExtension.BOX_VECTORS: vectors1},
                    {CUBAExtension.BOX_VECTORS: vectors2}])

    def test_get_box_command_format(self):
        vectors = [(10.0, 0.0, 0.0),
                   (0.0, 10.0, 0.0),
                   (0.0, 0.0, 10.0)]

        results = get_box([{CUBAExtension.BOX_VECTORS: vectors}]).split()

        assert_almost_equal(float(results[0]), 0.0)
        assert_almost_equal(float(results[4]), 0.0)
        assert_almost_equal(float(results[8]), 0.0)

        assert_almost_equal(float(results[1]), vectors[0][0])
        assert_almost_equal(float(results[5]), vectors[1][1])
        assert_almost_equal(float(results[9]), vectors[2][2])

        self.assertEqual(results[2], "xlo")
        self.assertEqual(results[6], "ylo")
        self.assertEqual(results[10], "zlo")

        self.assertEqual(results[3], "xhi")
        self.assertEqual(results[7], "yhi")
        self.assertEqual(results[11], "zhi")

        origin = (-1.0, 1.0, -1.0)
        results = get_box([{CUBAExtension.BOX_VECTORS: vectors,
                            CUBAExtension.BOX_ORIGIN: origin}]).split()

        assert_almost_equal(float(results[0]), origin[0])
        assert_almost_equal(float(results[4]), origin[1])
        assert_almost_equal(float(results[8]), origin[2])

        assert_almost_equal(float(results[1]), vectors[0][0]+origin[0])
        assert_almost_equal(float(results[5]), vectors[1][1]+origin[1])
        assert_almost_equal(float(results[9]), vectors[2][2]+origin[2])


if __name__ == '__main__':
    unittest.main()
