import unittest
from functools import partial

from simphony.core.cuba import CUBA
from simphony.cuds.particles import Particle
from simphony.testing.abc_check_particles import (
    CheckAddingParticles, CheckManipulatingParticles)
from simphony.testing.utils import (
    compare_particles, create_particles, create_particles_with_id)

from simlammps.lammps_wrapper import LammpsWrapper
from simlammps.testing.md_example_configurator import MDExampleConfigurator
from simlammps.common.atom_style_description import get_all_cuba_attributes
from simlammps.common.atom_style import AtomStyle


class TestFileIoParticlesAddParticles(
        CheckAddingParticles, unittest.TestCase):

    def supported_cuba(self):
        return get_all_cuba_attributes(AtomStyle.ATOMIC)

    def container_factory(self, name):
        self.wrapper.add_dataset(self.configurator.get_empty_particles(name))
        return self.wrapper.get_dataset(name)

    def setUp(self):
        self.configurator = MDExampleConfigurator()
        self.wrapper = LammpsWrapper(use_internal_interface=False)
        self.configurator.configure_wrapper(self.wrapper)
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
        return get_all_cuba_attributes(AtomStyle.ATOMIC)

    def container_factory(self, name):
        self.wrapper.add_dataset(self.configurator.get_empty_particles(name))
        return self.wrapper.get_dataset(name)

    def setUp(self):
        self.configurator = MDExampleConfigurator()
        self.wrapper = LammpsWrapper(use_internal_interface=True)
        self.configurator.configure_wrapper(self.wrapper)

        # Instead of calling CheckAddingParticles.setUp(self), we do the
        # same steps and also ensure the created particles have a data with
        # correct attributes (and values) for MD. Specifically, we use
        # a correct material uid.
        self.addTypeEqualityFunc(
            Particle, partial(compare_particles, testcase=self))
        self.particle_list = create_particles(restrict=self.supported_cuba())

        material = self.configurator.materials[0]
        for p in self.particle_list:
            p.data[CUBA.MATERIAL_TYPE] = material.uid

        self.container = self.container_factory('foo')
        self.ids = self.container.add_particles(self.particle_list)

    # TODO workaround for simphony issue #202 ( simphony/simphony-common#202 )
    def test_add_multiple_particles_with_id(self):

        # given
        container = self.container
        particles = create_particles_with_id(restrict=self.supported_cuba())

        # fix particles so that they have the right attributes
        # for lammps (MD)
        material = self.configurator.materials[0]
        for p in self.particles:
            p.data[CUBA.MATERIAL_TYPE] = material.uid

        # when
        uids = self.container.add_particles(particles)

        # then
        for particle in particles:
            uid = particle.uid
            self.assertIn(uid, uids)
            self.assertTrue(container.has_particle(uid))
            self.assertEqual(container.get_particle(uid), particle)


class TestFileIoParticlesManipulatingParticles(
        CheckManipulatingParticles, unittest.TestCase):

    def supported_cuba(self):
        return get_all_cuba_attributes(AtomStyle.ATOMIC)

    def container_factory(self, name):
        self.wrapper.add_dataset(self.configurator.get_empty_particles(name))
        return self.wrapper.get_dataset(name)

    def setUp(self):
        self.configurator = MDExampleConfigurator()
        self.wrapper = LammpsWrapper(use_internal_interface=False)
        self.configurator.configure_wrapper(self.wrapper)
        CheckManipulatingParticles.setUp(self)


class TestInternalParticlesManipulatingParticles(
        CheckManipulatingParticles, unittest.TestCase):

    def setUp(self):
        self.configurator = MDExampleConfigurator()
        self.wrapper = LammpsWrapper(use_internal_interface=True)
        self.configurator.configure_wrapper(self.wrapper)

        # Instead of calling CheckManipulatingParticles.setUp(self), we do the
        # same steps and also ensure the created particles have a data with
        # correct attributes (and values) for MD. Specifically, we use
        # a correct material uid.
        self.addTypeEqualityFunc(
            Particle, partial(compare_particles, testcase=self))
        self.particle_list = create_particles(restrict=self.supported_cuba())

        material = self.configurator.materials[0]
        for p in self.particle_list:
            p.data[CUBA.MATERIAL_TYPE] = material.uid

        self.container = self.container_factory('foo')
        self.ids = self.container.add_particles(self.particle_list)

    def supported_cuba(self):
        return get_all_cuba_attributes(AtomStyle.ATOMIC)

    def container_factory(self, name):
        self.wrapper.add_dataset(self.configurator.get_empty_particles(name))
        return self.wrapper.get_dataset(name)


if __name__ == '__main__':
    unittest.main()
