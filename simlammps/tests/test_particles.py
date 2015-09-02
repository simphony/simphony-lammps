import unittest

from simphony.cuds.particles import Particles
from simphony.core.cuba import CUBA

from simphony.testing.abc_check_particles import (
    ContainerAddParticlesCheck, ContainerManipulatingParticlesCheck)

from simlammps.lammps_wrapper import LammpsWrapper
from simlammps.testing.md_example_configurator import MDExampleConfigurator

# list of CUBA that is supported/needed by particles in LAMMPS-MD
_SUPPORTED_CUBA = [CUBA.VELOCITY]


class TestFileIoParticlesAddParticles(
        ContainerAddParticlesCheck, unittest.TestCase):

    def supported_cuba(self):
        return _SUPPORTED_CUBA

    def container_factory(self, name):
        return self.pc

    def setUp(self):
        self.wrapper = LammpsWrapper(use_internal_interface=False)
        MDExampleConfigurator.configure_wrapper(self.wrapper)
        pcs = [pc for pc in self.wrapper.iter_particles()]
        self.pc = pcs[0]
        ContainerAddParticlesCheck.setUp(self)


class TestInternalParticlesAddParticles(
        ContainerAddParticlesCheck, unittest.TestCase):

    def supported_cuba(self):
        return _SUPPORTED_CUBA

    def container_factory(self, name):
        return self.pc

    def setUp(self):
        self.wrapper = LammpsWrapper(use_internal_interface=True)
        MDExampleConfigurator.configure_wrapper(self.wrapper)
        pcs = [pc for pc in self.wrapper.iter_particles()]
        self.pc = pcs[0]
        ContainerAddParticlesCheck.setUp(self)


class TestFileIoParticlesManipulatingParticles(
        ContainerManipulatingParticlesCheck, unittest.TestCase):

    def supported_cuba(self):
        return _SUPPORTED_CUBA

    def container_factory(self, name):
        p = Particles(name="foo")
        pc_w = MDExampleConfigurator.add_configure_particles(self.wrapper,
                                                             p)
        return pc_w

    def setUp(self):
        self.wrapper = LammpsWrapper(use_internal_interface=False)
        MDExampleConfigurator.configure_wrapper(self.wrapper)
        ContainerManipulatingParticlesCheck.setUp(self)


class TestInternalParticlesManipulatingParticles(
        ContainerManipulatingParticlesCheck, unittest.TestCase):

    def supported_cuba(self):
        return _SUPPORTED_CUBA

    def container_factory(self, name):
        p = Particles(name="foo")
        pc_w = MDExampleConfigurator.add_configure_particles(self.wrapper,
                                                             p)
        return pc_w

    def setUp(self):
        self.wrapper = LammpsWrapper(use_internal_interface=True)
        MDExampleConfigurator.configure_wrapper(self.wrapper)
        ContainerManipulatingParticlesCheck.setUp(self)


if __name__ == '__main__':
    unittest.main()
