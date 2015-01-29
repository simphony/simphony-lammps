import unittest

from simphony.cuds.particles import Particle
from simlammps.lammps_wrapper import LammpsWrapper
from simlammps.tests.example_configurator import ExampleConfigurator


def _get_particle(particle_container):
    for p in particle_container.iter_particles():
        return p
    else:
        raise Exception("could not find a particle to test with")


class TestLammpsParticleContainer(unittest.TestCase):

    def setUp(self):

        self.wrapper = LammpsWrapper()

        # configuration is being done by dummy class
        # the wrapper is properly configured with
        # CM/SP/BC and given particles
        ExampleConfigurator.configure_wrapper(self.wrapper)

        # keep track of first wrapper-based particle container
        # and the particle ids that it contains
        pcs = [pc for _, pc in self.wrapper.iter_particle_containers()]
        self.pc = pcs[0]
        self.particle_ids_in_pc = []
        for p in pcs[0].iter_particles():
            self.particle_ids_in_pc.append(p.id)

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

    def test_iter_particles(self):
        iterated_ids = []
        for particle in self.pc.iter_particles():
            iterated_ids.append(particle.id)

        self.assertEqual(set(self.particle_ids_in_pc), set(iterated_ids),
                         'Error: incorrect iteration!')

        # make different list of ids to test with
        ids = self.particle_ids_in_pc
        ids = ids[0:3]

        iterated_ids = []
        for particle in self.pc.iter_particles(ids):
            iterated_ids.append(particle.id)

        self.assertEqual(set(ids), set(iterated_ids),
                         'Error: incorrect iteration! {0}---\n{1}'
                         .format(ids, iterated_ids))

if __name__ == '__main__':
    unittest.main()
