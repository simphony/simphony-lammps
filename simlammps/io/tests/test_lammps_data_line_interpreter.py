import unittest

from simphony.core.cuba import CUBA
from simlammps.io.lammps_data_line_interpreter import \
    (LammpsDataLineInterpreter, AtomStyle)


class TestLammpsDataLineInterpreter(unittest.TestCase):

    def test_interpret_atomic(self):
        interpreter = LammpsDataLineInterpreter(atom_style=AtomStyle.ATOMIC)

        # Atoms # atomic
        # 1 3 1.00000000000e+00 1.100000000e+00 1.000000000e+00 0 0 0
        atomic_values = [3, 1.0e+00, 1.1e+00, 1.0e+00, 0, 0, 0]
        coordinates, data = interpreter.convert_atom_values(atomic_values)
        self.assertEqual(coordinates, tuple(atomic_values[1:4]))
        self.assertEqual(data[CUBA.MATERIAL_TYPE], atomic_values[0])

    def test_interpret_sphere(self):
        interpreter = LammpsDataLineInterpreter(atom_style=AtomStyle.SPHERE)

        # Atoms # sphere
        # 1 1 0.5 1.000000000000e+00 -5.0 0.0 0.00000000e+00 0 0 0
        # 2 1 0.5 1.000000000000e+00 10.0 0.0 0.00000000e+00 0 0 0
        atomic_values = [1, 0.5, 1.000000e+00, -5.0, 0.0, 0.0000e+00, 0, 0, 0]
        coordinates, data = interpreter.convert_atom_values(atomic_values)
        self.assertEqual(coordinates, tuple(atomic_values[3:6]))
        self.assertEqual(data[CUBA.MATERIAL_TYPE], atomic_values[0])
        self.assertEqual(data[CUBA.RADIUS], atomic_values[1]/2)
        self.assertEqual(data[CUBA.DENSITY], atomic_values[2])


if __name__ == '__main__':
    unittest.main()
