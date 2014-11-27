import unittest
import shutil

from simlammps.lammps_wrapper import LammpsWrapper
from simphony.cuds.particles import Particle


def _get_particle(particle_container):
    for p in particle_container.iter_particles():
        return p
    else:
        raise Exception("could not find a particle to test with")


class TestLammpsFileParticleContainer(unittest.TestCase):

    def setUp(self):

        self.wrapper = LammpsWrapper()

        # TODO replace.  use available methods (e.g. add_particle)
        # to properly configure the data
        shutil.copyfile("examples/flow/original_input.data", "data.lammps")
        self.wrapper.dummy_init_data()

        for name, pc in self.wrapper.iter_particle_containers():
            self.pc = pc
            break
        else:
            self.fail("no particle containers to test with")

    def test_update_non_existing_particle(self):
        with self.assertRaises(Exception):
            p = Particle(id=100000000, coordinates=(0.0, 0.0, 0.0))
            self.pc.update_particle(p)

    def test_get_non_existing_particle(self):
        with self.assertRaises(Exception):
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
        self.pc.remove_particle(removed_particle)

        # check that it was removed
        with self.assertRaises(Exception):
            self.pc.get_particle(removed_particle)

        self.wrapper.run()

        # check that it stayed removed
        with self.assertRaises(Exception):
            self.pc.get_particle(removed_particle)

if __name__ == '__main__':
    unittest.main()
