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


if __name__ == '__main__':
    unittest.main()
