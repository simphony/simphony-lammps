import unittest

from simphony.cuds.particles import Particles
from simphony.core.cuba import CUBA

from simphony.testing.abc_check_particles import (
    CheckAddingParticles, CheckManipulatingParticles)
from simphony.testing.utils import create_particles_with_id

from simlammps.lammps_wrapper import LammpsWrapper
from simlammps.testing.md_example_configurator import MDExampleConfigurator

# list of CUBA that is supported/needed by particles in LAMMPS-MD
_SUPPORTED_CUBA = [CUBA.VELOCITY]


class TestFileIoParticlesAddParticles(
        CheckAddingParticles, unittest.TestCase):

    def supported_cuba(self):
        return _SUPPORTED_CUBA

    def container_factory(self, name):
        return self.pc

    def setUp(self):
        self.wrapper = LammpsWrapper(use_internal_interface=False)
        MDExampleConfigurator.configure_wrapper(self.wrapper)
        pcs = [pc for pc in self.wrapper.iter_datasets()]
        self.pc = pcs[0]
        CheckAddingParticles.setUp(self)

    # TODO workaround for simphony issue #202 ( simphony/simphony-common#202 )
    def test_add_multiple_particles_with_id(self):
        # given
        container = self.container
        particles = create_particles_with_id(restrict=self.supported_cuba())

        # when
        uids = container.add_particles(particles)

        # then
        for particle in particles:
            uid = particle.uid
            self.assertIn(uid, uids)
            self.assertTrue(container.has_particle(uid))
            self.assertEqual(container.get_particle(uid), particle)


class TestInternalParticlesAddParticles(
        CheckAddingParticles, unittest.TestCase):

    def supported_cuba(self):
        return _SUPPORTED_CUBA

    def container_factory(self, name):
        return self.pc

    def setUp(self):
        self.wrapper = LammpsWrapper(use_internal_interface=True)
        MDExampleConfigurator.configure_wrapper(self.wrapper)
        pcs = [pc for pc in self.wrapper.iter_datasets()]
        self.pc = pcs[0]
        CheckAddingParticles.setUp(self)

    # TODO workaround for simphony issue #202 ( simphony/simphony-common#202 )
    def test_add_multiple_particles_with_id(self):
        # given
        container = self.container
        particles = create_particles_with_id(restrict=self.supported_cuba())

        # when
        uids = container.add_particles(particles)

        # then
        for particle in particles:
            uid = particle.uid
            self.assertIn(uid, uids)
            self.assertTrue(container.has_particle(uid))
            self.assertEqual(container.get_particle(uid), particle)


class TestFileIoParticlesManipulatingParticles(
        CheckManipulatingParticles, unittest.TestCase):

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
        CheckManipulatingParticles.setUp(self)


class TestInternalParticlesManipulatingParticles(
        CheckManipulatingParticles, unittest.TestCase):

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
        CheckManipulatingParticles.setUp(self)


if __name__ == '__main__':
    unittest.main()
