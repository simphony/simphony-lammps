import unittest
import tempfile
import shutil
import os

from numpy.testing import assert_almost_equal

from simphony.core.cuba import CUBA

from simlammps.io.file_utility import read_data_file
from simlammps.cuba_extension import CUBAExtension


class TestFileUtility(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tear_down(self):
        shutil.rmtree(self.temp_dir)

    def test_read_data_file(self):
        filename = os.path.join(self.temp_dir, "test_data.txt")
        _write_example_file(filename, _data_file_contents)

        particles_list = read_data_file(filename)
        self.assertEqual(3, len(particles_list))

        masses = set(particles.data[CUBA.MASS] for particles in particles_list)
        self.assertEqual(masses, set([3, 42, 1]))

        number_particles = 0
        for particles in particles_list:
            number_particles += sum(1 for _ in particles.iter_particles())
            assert_almost_equal(
                particles.data_extension[CUBAExtension.BOX_ORIGIN],
                (0.0000000000000000e+00,
                 -2.2245711031688635e-03,
                 -3.2108918131150160e-01))
            box = [(2.5687134504920127e+01, 0.0, 0.0),
                   (0.0, 2.2247935602791809e+01+2.2245711031688635e-03, 0.0),
                   (0.0, 0.0, 3.2108918131150160e-01-(-3.210891813115016e-01))]
            assert_almost_equal(
                particles.data_extension[CUBAExtension.BOX_VECTORS],
                box)

            for p in particles.iter_particles():
                assert_almost_equal(p.data[CUBA.VELOCITY], [1.0, 1.0, 1.0])

        self.assertEqual(4, number_particles)


def _write_example_file(filename, contents):
    with open(filename, "w") as text_file:
            text_file.write(contents)

_data_file_contents = """LAMMPS data file via write_data, version 28 Jun 2014, timestep = 0

4 atoms
3 atom types

0.0000000000000000e+00 2.5687134504920127e+01 xlo xhi
-2.2245711031688635e-03 2.2247935602791809e+01 ylo yhi
-3.2108918131150160e-01 3.2108918131150160e-01 zlo zhi

Masses

1 3
2 42
3 1

Pair Coeffs # lj/cut

1 1 1
2 1 1

Atoms # atomic

1 3 1.0000000000000000e+00 1.0000000000000000e+00 1.0000000000000000e+00 0 0 0
2 1 2.0000000000000000e+00 2.0000000000000000e+00 2.0000000000000000e+00 0 0 0
3 3 3.0000000000000000e+00 3.0000000000000000e+00 3.0000000000000000e+00 0 0 0
4 2 4.0000000000000000e+00 4.0000000000000000e+00 4.0000000000000000e+00 0 0 0

Velocities

1 1.0000000000000000e+00 1.0000000000000000e+00 1.0000000000000000e+00
2 1.0000000000000000e+00 1.0000000000000000e+00 1.0000000000000000e+00
3 1.0000000000000000e+00 1.0000000000000000e+00 1.0000000000000000e+00
4 1.0000000000000000e+00 1.0000000000000000e+00 1.0000000000000000e+00"""

if __name__ == '__main__':
    unittest.main()
