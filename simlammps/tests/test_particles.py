import unittest

from simphony.cuds.particles import Particles
from simlammps.lammps_wrapper import LammpsWrapper, InterfaceType
from simlammps.testing.md_example_configurator import MDExampleConfigurator

# using the following tests instead of those
# located in simphony.testing as we currently
# dont pass all tests
from simlammps.testing.abc_check_particles import (
    ContainerAddParticlesCheck, ContainerManipulatingParticlesCheck)

# list of CUBA that is supported by particles in LAMMPS-MD
# TODO add CUBA.VELOCITY
_supported_cuba = []


class TestFileIoParticlesAddParticles(
        ContainerAddParticlesCheck, unittest.TestCase):

    def container_factory(self, name):
        return self.pc

    def setUp(self):
        self.wrapper = LammpsWrapper(interface=InterfaceType.FILEIO)
        MDExampleConfigurator.configure_wrapper(self.wrapper)
        pcs = [pc for pc in self.wrapper.iter_particles()]
        self.pc = pcs[0]
        ContainerAddParticlesCheck.setUp(self, restrict=_supported_cuba)


class TestInternalParticlesAddParticles(
        ContainerAddParticlesCheck, unittest.TestCase):

    def container_factory(self, name):
        return self.pc

    def setUp(self):
        self.wrapper = LammpsWrapper(interface=InterfaceType.INTERNAL)
        MDExampleConfigurator.configure_wrapper(self.wrapper)
        pcs = [pc for pc in self.wrapper.iter_particles()]
        self.pc = pcs[0]
        ContainerAddParticlesCheck.setUp(self, restrict=_supported_cuba)


class TestFileIoParticlesManipulatingParticles(
        ContainerManipulatingParticlesCheck, unittest.TestCase):

    def container_factory(self, name):
        p = Particles(name="foo")
        pc_w = MDExampleConfigurator.add_configure_particles(self.wrapper,
                                                             p)
        return pc_w

    def setUp(self):
        self.wrapper = LammpsWrapper(interface=InterfaceType.FILEIO)
        MDExampleConfigurator.configure_wrapper(self.wrapper)
        ContainerManipulatingParticlesCheck.setUp(self,
                                                  restrict=_supported_cuba)


class TestInternalParticlesManipulatingParticles(
        ContainerManipulatingParticlesCheck, unittest.TestCase):

    def container_factory(self, name):
        p = Particles(name="foo")
        pc_w = MDExampleConfigurator.add_configure_particles(self.wrapper,
                                                             p)
        return pc_w

    def setUp(self):
        self.wrapper = LammpsWrapper(interface=InterfaceType.INTERNAL)
        MDExampleConfigurator.configure_wrapper(self.wrapper)
        ContainerManipulatingParticlesCheck.setUp(self,
                                                  restrict=_supported_cuba)


if __name__ == '__main__':
    unittest.main()
