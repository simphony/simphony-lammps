"""Tests for running lammps using CUDS and Simulation classes."""
import unittest

from simphony.api import CUDS, Simulation
from simphony.core.cuba import CUBA
from simphony.cuds.meta import api
from simphony.cuds.particles import Particles
from simphony.engine import EngineInterface
from simphony.testing.utils import create_particles_with_id


class LAMMPSCUDSTestCase(unittest.TestCase):
    def setUp(self):
        self.cuds = self.generate_cuds()

    def generate_cuds(self):
        pset1 = create_particles_with_id(restrict=[CUBA.VELOCITY])
        for p in pset1:
            p.data[CUBA.MATERIAL_TYPE] = 1

        pset2 = create_particles_with_id(restrict=[CUBA.VELOCITY])
        for p in pset2:
            p.data[CUBA.MATERIAL_TYPE] = 1

        ps1 = Particles('ps1')
        ps2 = Particles('ps2')

        ps1.add(pset1)
        ps2.add(pset2)

        c = CUDS()
        c.add([ps2])

        mat = api.Material()
        mat.data[CUBA.MASS] = 1.0
        c.add([mat])

        box = api.Box()
        c.add([box])

        return c

    # def test_create_lammps_internal_simulation(self):
    #     self.assertRaisesRegexp(RuntimeError,
    #                             'CUBAExtension.BOX_VECTORS',
    #                             Simulation,
    #                             self.cuds,
    #                             'LAMMPS',
    #                             EngineInterface.Internal)

    # def test_create_lammps_fileio_simulation(self):
    #     sim = Simulation(self.cuds, 'LAMMPS', EngineInterface.FileIO)
    #     self.assertEqual(self.cuds, sim.get_cuds())
