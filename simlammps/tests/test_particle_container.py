import unittest
from simphony.cuds.particles import Particle
from simphony.core.cuba import CUBA

from simlammps.lammps_wrapper import LammpsWrapper
from simlammps.dummy import LammpsDummyConfig


def _get_particle(particle_container):
    for p in particle_container.iter_particles():
        return p
    else:
        raise Exception("could not find a particle to test with")


class TestLammpsParticleContainer(unittest.TestCase):

    def setUp(self):

        self.wrapper = LammpsWrapper()
        self.wrapper.CM[CUBA.NUMBEROF_TIME_STEPS] = 10000

        # TODO:  change once wrapper cm/sp/bc are being properly
        # configured.

        # add some particle containers
        pcs_wrapper = []
        for i, pc in LammpsDummyConfig.get_particle_containers().iteritems():
            pcs_wrapper.append(self.wrapper.add_particle_container(str(i), pc))

        self.pc = pcs_wrapper[0]

    def test_update_non_existing_particle(self):
        with self.assertRaises(KeyError):
            p = Particle(id=100000000, coordinates=(0.0, 0.0, 0.0))
            self.pc.update_particle(p)

    def test_get_non_existing_particle(self):
        with self.assertRaises(KeyError):
            self.pc.get_particle(100000000)

    def test_update_particle(self):
        particle = _get_particle(self.pc)
        particle.coordinates = (42.0, 42.0, 42.0)
        self.pc.update_particle(particle)
        updated_p = self.pc.get_particle(particle.id)

        self.assertEqual(particle.coordinates, updated_p.coordinates)

    def test_add_particle_without_id(self):
        p = Particle(coordinates=(0.0, 2.5, 0.0))
        id = self.pc.add_particle(p)
        added_p = self.pc.get_particle(id)
        self.assertEqual(p.coordinates, added_p.coordinates)

    def test_delete_particle(self):
        removed_particle = _get_particle(self.pc)
        self.pc.remove_particle(removed_particle.id)

        # check that it was removed
        with self.assertRaises(KeyError):
            self.pc.get_particle(removed_particle.id)

        self.wrapper.run()

        # check that it stayed removed
        with self.assertRaises(KeyError):
            self.pc.get_particle(removed_particle.id)

if __name__ == '__main__':
    unittest.main()
