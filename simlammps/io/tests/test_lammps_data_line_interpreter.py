import unittest

from simphony.core.cuba import CUBA

from simlammps.common.atom_style import AtomStyle
from simlammps.io.lammps_data_line_interpreter import LammpsDataLineInterpreter


class TestLammpsDataLineInterpreter(unittest.TestCase):

    def test_interpret_atomic_atoms(self):
        interpreter = LammpsDataLineInterpreter(atom_style=AtomStyle.ATOMIC)

        # Atoms # atomic
        # 1 3 1.00000000000e+00 1.100000000e+00 1.000000000e+00 0 0 0
        atomic_values = [3, 1.0e+00, 1.1e+00, 1.0e+00, 0, 0, 0]
        coordinates, data = interpreter.convert_atom_values(atomic_values)
        self.assertEqual(coordinates, tuple(atomic_values[1:4]))
        self.assertEqual(data[CUBA.MATERIAL_TYPE], atomic_values[0])

    def test_interpret_sphere_atoms(self):
        interpreter = LammpsDataLineInterpreter(atom_style=AtomStyle.SPHERE)

        # Atoms # sphere
        # 1 1 0.5 1.000000000000e+00 -5.0 0.0 0.00000000e+00 0 0 0
        atomic_values = [1, 0.5, 1.000000e+00, -5.0, 0.0, 0.0000e+00, 0, 0, 0]
        coordinates, data = interpreter.convert_atom_values(atomic_values)
        self.assertEqual(coordinates, tuple(atomic_values[3:6]))
        self.assertEqual(data[CUBA.MATERIAL_TYPE], atomic_values[0])
        self.assertEqual(data[CUBA.RADIUS], atomic_values[1]/2)
        self.assertEqual(data[CUBA.MASS], atomic_values[2])

    def test_interpret_atomic_velocities(self):
        interpreter = LammpsDataLineInterpreter(atom_style=AtomStyle.ATOMIC)

        # Velocities
        # 1 0.00000000000e+00 0.100000000e+00 0.200000000e+00
        velocity_values = [0.0, 0.1, 0.2]
        data = interpreter.convert_velocity_values(velocity_values)
        self.assertEqual(data[CUBA.VELOCITY],
                         tuple(velocity_values[0:3]))

    def test_interpret_sphere_velocities(self):
        interpreter = LammpsDataLineInterpreter(atom_style=AtomStyle.SPHERE)

        # Velocities
        # 1 0.0000000e+00 0.100000e+00 0.200000000e+00 2.0e+00 2.1e+00 2.2e+00
        velocity_values = [0.0, 0.1, 0.2, 2.0, 2.1, 2.2]
        data = interpreter.convert_velocity_values(velocity_values)
        self.assertEqual(data[CUBA.VELOCITY],
                         tuple(velocity_values[0:3]))
        self.assertEqual(data[CUBA.ANGULAR_VELOCITY],

                         tuple(velocity_values[3:6]))


if __name__ == '__main__':
    unittest.main()
