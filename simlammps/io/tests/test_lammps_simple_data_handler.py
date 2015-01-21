import unittest
import tempfile
import shutil
import os

from simlammps.io.lammps_data_file_parser import LammpsDataFileParser
from simlammps.io.lammps_simple_data_handler import LammpsSimpleDataHandler


class TestLammpsSimpleDataHandler(unittest.TestCase):
    """ Tests the data reader class

    """
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

        self.handler = LammpsSimpleDataHandler()
        self.parser = LammpsDataFileParser(handler=self.handler)
        self.filename = os.path.join(self.temp_dir, "test_data.txt")

        _write_example_file(self.filename, _data_file_contents)

    def tear_down(self):
        shutil.rmtree(self.temp_dir)

    def test_number_atom_types(self):
        self.parser.parse(self.filename)
        self.assertEqual(3, self.handler.get_number_atom_types())

    def test_masses(self):
        self.parser.parse(self.filename)
        masses = self.handler.get_masses()
        self.assertEqual(len(masses), self.handler.get_number_atom_types())
        self.assertEqual(masses[1], 3)
        self.assertEqual(masses[2], 42)
        self.assertEqual(masses[3], 1)

    def test_atoms(self):
        self.parser.parse(self.filename)
        atoms = self.handler.get_atoms()

        for i in range(1, 4):
            self.assertTrue(i in atoms)
            self.assertEqual(atoms[i][1:4], [i * 1.0, i * 1.0, i * 1.0])

    def test_velocties(self):
        self.parser.parse(self.filename)
        velocities = self.handler.get_velocities()

        for i in range(1, 4):
            self.assertTrue(i in velocities)
            self.assertEqual(velocities[i], [i * 1.0, i * 1.0, i * 1.0])


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
3 1 1

Atoms # atomic

1 1 1.0000000000000000e+00 1.0000000000000000e+00 1.0000000000000000e+00 0 0 0
2 2 2.0000000000000000e+00 2.0000000000000000e+00 2.0000000000000000e+00 0 0 0
3 3 3.0000000000000000e+00 3.0000000000000000e+00 3.0000000000000000e+00 0 0 0
4 2 4.0000000000000000e+00 4.0000000000000000e+00 4.0000000000000000e+00 0 0 0

Velocities

1 1.0000000000000000e+00 1.0000000000000000e+00 1.0000000000000000e+00
2 2.0000000000000000e+00 2.0000000000000000e+00 2.0000000000000000e+00
3 3.0000000000000000e+00 3.0000000000000000e+00 3.0000000000000000e+00
4 4.0000000000000000e+00 4.0000000000000000e+00 4.0000000000000000e+00"""

if __name__ == '__main__':
    unittest.main()
