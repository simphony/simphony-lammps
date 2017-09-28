import os
import shutil
import tempfile
import unittest

import numpy
from numpy.testing import assert_almost_equal
from simphony.api import CUBA
from simphony.core.keywords import KEYWORDS

from simlammps.common.atom_style import AtomStyle
from simlammps.common.atom_style_description import get_all_cuba_attributes
from simlammps.io.file_utility import (read_data_file,
                                       write_data_file)



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
        particles, SD = read_data_file(self._write_example_file(
            _explicit_atomic_style_file_contents))

        masses =\
            [material.data[CUBA.MASS] for material
             in SD.iter(item_type=CUBA.MATERIAL)]
        self.assertItemsEqual(masses, [3, 42, 1])

        self.assertEqual(4, particles.count_of(CUBA.PARTICLE))
        assert_almost_equal(
            particles.data[CUBA.ORIGIN],
            (0.0000000000000000e+00,
             -2.2245711031688635e-03,
             -3.2108918131150160e-01))
        box = [(2.5687134504920127e+01, 0.0, 0.0),
               (0.0, 2.2247935602791809e+01 + 2.2245711031688635e-03, 0.0),
               (0.0, 0.0, 3.2108918131150160e-01 - (-3.210891813115016e-01))]
        assert_almost_equal(
            particles.data[CUBA.VECTOR],
            box)

        for p in particles.iter(item_type=CUBA.PARTICLE):
            assert_almost_equal(p.data[CUBA.VELOCITY], [1.0, 1.0, 1.0])

    def test_read_sphere_style_data_file(self):
        # when
        particles, SD = read_data_file(self._write_example_file(
            _explicit_sphere_style_file_contents))

        # then
        self.assertEqual(3, particles.count_of(CUBA.PARTICLE))

        assert_almost_equal(
            particles.data[CUBA.ORIGIN],
            (-10.0, -7.500, -0.500))
        box = [(25.0, 0.0, 0.0),
               (0.0, 15.0, 0.0),
               (0.0, 0.0, 1.0)]
        assert_almost_equal(
            particles.data[CUBA.VECTOR],
            box)

        for p in particles.iter(item_type=CUBA.PARTICLE):
            assert_almost_equal(p.data[CUBA.ANGULAR_VELOCITY], [0.0, 0.0, 1.0])
            assert_almost_equal(p.data[CUBA.VELOCITY], [5.0, 0.0, 0.0])
            assert_almost_equal(p.data[CUBA.RADIUS], 0.5 / 2)
            assert_almost_equal(p.data[CUBA.MASS], 1.0)

    def test_write_file_sphere(self):
        # given
        original_particles, SD = read_data_file(self._write_example_file(
            _explicit_sphere_style_file_contents))
        output_filename = os.path.join(self.temp_dir, "output.txt")

        # when
        write_data_file(filename=output_filename,
                        particles=original_particles,
                        state_data=SD,
                        atom_style=AtomStyle.SPHERE)

        # then
        read_particles, SD = read_data_file(output_filename)

        _compare_particles_averages(read_particles,
                                    original_particles,
                                    get_all_cuba_attributes(
                                        AtomStyle.SPHERE),
                                    self)

    def test_write_file_atom(self):
        # given
        original_particles, SD = read_data_file(self._write_example_file(
            _explicit_atomic_style_file_contents))
        output_filename = os.path.join(self.temp_dir, "output.txt")

        # when
        write_data_file(filename=output_filename,
                        particles=original_particles,
                        state_data=SD,
                        atom_style=AtomStyle.ATOMIC)

        # then
        read_particles, SD = read_data_file(output_filename)
        _compare_particles_averages(read_particles,
                                    original_particles,
                                    get_all_cuba_attributes(AtomStyle.ATOMIC),
                                    self)


def _compare_particles_averages(particles,
                                reference,
                                attributes_keys,
                                testcase):
    """  Compares average values (velocity, etc) of two Particles

    This comparison compares the average values of two Particles, which is
    useful when comparing two Particles who are representing the same thing but
    whose particle id's are different.

    """
    self = testcase

    len_particles = particles.count_of(CUBA.PARTICLE)
    len_reference = reference.count_of(CUBA.PARTICLE)
    self.assertEqual(len_particles, len_reference)
    for key in attributes_keys:
        keyword = KEYWORDS[CUBA(key).name]

        # TODO remove this as we are missuing MATERIAL_TYPE for our uid
        #  (so it has a type of 'int' but we are using it to store uids)
        if key == CUBA.MATERIAL_TYPE:
            continue

        if (keyword.dtype == numpy.float64 or keyword.dtype == numpy.int32):
            average_particles = _get_average(particles, key, keyword.shape)
            average_reference = _get_average(reference, key, keyword.shape)
            assert_almost_equal(average_particles, average_reference)


def _get_average(particles, key, shape):
    """ Get average value for a particular CUBA key

    Parameters:
    -----------
    key : CUBA
        key of value
    shape : shape
        shape of value

    """
    length = particles.count_of(CUBA.PARTICLE)

    if shape == [1]:
        return sum(p.data[key] for p in
                   particles.iter(item_type=CUBA.PARTICLE)) / length
    else:
        return tuple(map(lambda y: sum(y) / float(len(y)), zip(
            *[p.data[key] for p in particles.iter(item_type=CUBA.PARTICLE)])))


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

Atoms # granular

1 1 0.5 1.0000000000000000e+00 -5.0 0.0 0.0000000000000000e+00 0 0 0
2 1 0.5 1.0000000000000000e+00 10.0 0.0 0.0000000000000000e+00 0 0 0
3 1 0.5 1.0000000000000000e+00 10.43330 0.25000 0.0000000000000000e+00 0 0 0

Velocities

1 5.0 0.0 0.0 0.0 0.0 1.0
2 5.0 0.0 0.0 0.0 0.0 1.0
3 5.0 0.0 0.0 0.0 0.0 1.0
"""

if __name__ == '__main__':
    unittest.main()
