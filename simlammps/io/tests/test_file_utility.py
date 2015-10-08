import unittest
import tempfile
import shutil
import os

from numpy.testing import assert_almost_equal

from simphony.core.cuba import CUBA
from simphony.core.cuds_item import CUDSItem

from simlammps.io.file_utility import read_data_file
from simlammps.cuba_extension import CUBAExtension


class TestFileUtility(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tear_down(self):
        shutil.rmtree(self.temp_dir)

    def _write_example_file(self, contents):
        filename = os.path.join(self.temp_dir, "test_data.txt")
        with open(filename, "w") as text_file:
            text_file.write(contents)
        return filename

    def test_read_atomic_style_data_file(self):
        particles_list = read_data_file(self._write_example_file(
            _explicit_atomic_style_file_contents))

        self.assertEqual(3, len(particles_list))

        masses = set(particles.data[CUBA.MASS] for particles in particles_list)
        self.assertEqual(masses, set([3, 42, 1]))

        total_number_particles = 0
        for particles in particles_list:
            total_number_particles += particles.count_of(CUDSItem.PARTICLE)
            self.assertEqual(str(particles.data[CUBA.MATERIAL_TYPE]),
                             particles.name)
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

        self.assertEqual(4, total_number_particles)

    def test_read_sphere_style_data_file(self):
        particles_list = read_data_file(self._write_example_file(
            _explicit_sphere_style_file_contents))
        self.assertEqual(1, len(particles_list))

        particles = particles_list[0]
        self.assertEqual(3, particles.count_of(CUDSItem.PARTICLE))
        self.assertEqual(str(particles.data[CUBA.MATERIAL_TYPE]),
                         particles.name)
        assert_almost_equal(
            particles.data_extension[CUBAExtension.BOX_ORIGIN],
            (-10.0, -7.500, -0.500))
        box = [(25.0, 0.0, 0.0),
               (0.0, 15.0, 0.0),
               (0.0, 0.0, 1.0)]
        assert_almost_equal(
            particles.data_extension[CUBAExtension.BOX_VECTORS],
            box)

        for p in particles.iter_particles():
            assert_almost_equal(p.data[CUBA.VELOCITY], [5.0, 0.0, 0.0])
            assert_almost_equal(p.data[CUBA.RADIUS], 0.5/2)
            assert_almost_equal(p.data[CUBA.DENSITY], 1.0)


_explicit_atomic_style_file_contents = """LAMMPS data file via write_data, version 28 Jun 2014, timestep = 0

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

_explicit_sphere_style_file_contents = """LAMMPS data file via write_data, version 28 Jun 2014, timestep = 25000

3 atoms
1 atom types

-10.0000000000000000e+00 15.0000000000000000e+00 xlo xhi
-7.5000000000000000e+00 7.5000000000000000e+00 ylo yhi
-5.0000000000000000e-01 5.0000000000000000e-01 zlo zhi

Atoms # sphere

1 1 0.5 1.0000000000000000e+00 -5.0 0.0 0.0000000000000000e+00 0 0 0
2 1 0.5 1.0000000000000000e+00 10.0 0.0 0.0000000000000000e+00 0 0 0
3 1 0.5 1.0000000000000000e+00 10.43330 0.25000 0.0000000000000000e+00 0 0 0

Velocities

1 5.0 0.0 0.0 0.0000000000000000e+00 0.0000000000000000e+00 0.0
2 5.0 0.0 0.0 0.0000000000000000e+00 0.0000000000000000e+00 0.0
3 5.0 0.0 0.0 0.0000000000000000e+00 0.0000000000000000e+00 0.0
"""

if __name__ == '__main__':
    unittest.main()
