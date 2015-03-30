import unittest

from simphony.cuds.particles import Particles
from simphony.testing.abc_check_particles import (
    ContainerAddParticlesCheck, ContainerManipulatingParticlesCheck)
from simlammps.lammps_wrapper import LammpsWrapper
from simlammps.testing.md_example_configurator import MDExampleConfigurator


class TestFileIoParticlesAddParticles(
        ContainerAddParticlesCheck, unittest.TestCase):

    def container_factory(self, name):
        return self.pc

    def setUp(self):
        self.wrapper = LammpsWrapper()
        MDExampleConfigurator.configure_wrapper(self.wrapper)
        pcs = [pc for pc in self.wrapper.iter_particles()]
        self.pc = pcs[0]
        ContainerAddParticlesCheck.setUp(self)


class TestFileIoParticlesManipulatingParticles(
        ContainerManipulatingParticlesCheck, unittest.TestCase):

    def container_factory(self, name):
        pc = Particles(name=name)
        return self.wrapper.add_particles(pc)

    def setUp(self):
        self.wrapper = LammpsWrapper()
        ContainerManipulatingParticlesCheck.setUp(self)


def _get_particle(particles):
    for p in particles.iter_particles():
        return p
    else:
        raise RuntimeError("could not find a particle to test with")


class TestLammpsParticles(unittest.TestCase):

    def setUp(self):
        self.wrapper = LammpsWrapper()

        # configuration is being done by dummy class
        # the wrapper is properly configured with
        # CM/SP/BC and given particles
        MDExampleConfigurator.configure_wrapper(self.wrapper)

        # keep track of first wrapper-based container of particles
        # and the particle ids that it contains
        pcs = [pc for pc in self.wrapper.iter_particles()]
        self.pc = pcs[0]
        self.particle_ids_in_pc = []
        for p in pcs[0].iter_particles():
            self.particle_ids_in_pc.append(p.uid)

    def test_delete_particle(self):
        removed_particle = _get_particle(self.pc)
        self.pc.remove_particle(removed_particle.uid)

        # check that it was removed
        with self.assertRaises(KeyError):
            self.pc.get_particle(removed_particle.uid)

        self.wrapper.run()

        # check that it stayed removed
        with self.assertRaises(KeyError):
            self.pc.get_particle(removed_particle.uid)

if __name__ == '__main__':
    unittest.main()
