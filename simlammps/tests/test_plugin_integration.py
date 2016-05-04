import unittest
import simphony.engine as engine_api
from simphony.engine import EngineInterface, create_wrapper

from simphony import CUDS
from simlammps.lammps_wrapper import LammpsWrapper


# TODO: Use an enum instead, defined in a proper place
_LAMMPS = 'LAMMPS'
_LIGGGHTS = 'LIGGGHTS'


class TestPluginIntegration(unittest.TestCase):
    """Plugin integration tests."""
    def test_plugin_integration(self):
        from simphony.engine import lammps
        self.assertTrue(hasattr(lammps, 'LammpsWrapper'))

    def test_engine_registration(self):
        self.assertIn(_LAMMPS, engine_api.get_supported_engine_names())
        self.assertIn(_LIGGGHTS, engine_api.get_supported_engine_names())

    def test_lammps_creation(self):
        cuds = CUDS()
        lammps = create_wrapper(cuds, _LAMMPS,
                                EngineInterface.Internal)
        self.assertIsInstance(lammps, LammpsWrapper)

        lammps = create_wrapper(cuds, _LAMMPS,
                                EngineInterface.FileIO)
        self.assertIsInstance(lammps, LammpsWrapper)

    def test_liggghts_creation(self):
        cuds = CUDS()
        lights = create_wrapper(cuds, _LIGGGHTS,
                                EngineInterface.FileIO)
        self.assertIsInstance(lights, LammpsWrapper)

        self.assertRaises(RuntimeError, create_wrapper, cuds,
                          _LIGGGHTS,
                          EngineInterface.Internal)


if __name__ == '__main__':
    unittest.main()
