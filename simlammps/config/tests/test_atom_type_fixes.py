import unittest

from simphony.core.cuba import CUBA
from simphony.cuds.meta.api import Material

from simlammps.config.atom_type_fixes import get_per_atom_type_fixes
from simlammps.common.atom_style import AtomStyle


class TestAtomTypeFixes(unittest.TestCase):

    def test_granular_style(self):
        # when
        materials = [Material(
            data={CUBA.YOUNG_MODULUS: float(i),
                  CUBA.POISSON_RATIO: float(i)}) for i in xrange(1, 3)]
        commands = get_per_atom_type_fixes(AtomStyle.GRANULAR, materials)
        lines = commands.rstrip("\n").split("\n")
        self.assertEqual(len(lines), 2)

    def test_atomic_style(self):
        materials = []
        commands = get_per_atom_type_fixes(AtomStyle.ATOMIC, materials)
        self.assertEqual(len(commands), 0)

    def test_granular_style_missing_materials(self):
        # when
        materials = []
        with self.assertRaises(ValueError):
            get_per_atom_type_fixes(AtomStyle.GRANULAR, materials)

    def test_granular_style_missing_required_cuba(self):
        # when
        materials = []
        with self.assertRaises(ValueError):
            get_per_atom_type_fixes(AtomStyle.GRANULAR, materials)


if __name__ == '__main__':
    unittest.main()
