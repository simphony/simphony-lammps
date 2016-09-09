import abc
from functools import partial

from numpy.testing import assert_almost_equal

from simphony.testing.utils import (
    compare_data_containers, compare_particles)
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA
from simphony.cuds.particles import Particle

from .md_example_configurator import MDExampleConfigurator


def _get_particle_and_dataset(wrapper):
    """
    get particle and particle container

    """
    for particles in wrapper.iter_datasets():
        for p in particles.iter_particles():
            return p, particles
    else:
        raise RuntimeError("could not find a particle to test with")


class ABCLammpsMDEngineCheck(object):

    __metaclass__ = abc.ABCMeta

    def setUp(self):
        self._md_configurator = MDExampleConfigurator()
        self.addTypeEqualityFunc(
            DataContainer, partial(compare_data_containers, testcase=self))
        self.addTypeEqualityFunc(
            Particle, partial(compare_particles, testcase=self))
        self.wrapper = self.engine_factory()

    @abc.abstractmethod
    def engine_factory(self):
        """ Create and return the engine
        """

    def test_run(self):
        self._md_configurator.configure_wrapper(self.wrapper)
        self.wrapper.run()

    def test_run_remove_particle(self):
        self._md_configurator.configure_wrapper(self.wrapper)

        removed_particle, particles = _get_particle_and_dataset(self.wrapper)
        particles.remove_particles([removed_particle.uid])

        # check that it was removed
        with self.assertRaises(KeyError):
            particles.get_particle(removed_particle.uid)

        self.wrapper.run()

        # check that it stayed removed
        with self.assertRaises(KeyError):
            particles.get_particle(removed_particle.uid)

    def test_0_step_run(self):
        self._md_configurator.configure_wrapper(self.wrapper)
        particles_uids = []
        foo = self._md_configurator.get_empty_particles("foo")
        material_uid = self._md_configurator._materials[0].uid
        for i in range(0, 5):
            p = Particle(coordinates=(1+0.1*i, 1+0.1*i, 0+0.1*i),
                         data={
                             CUBA.VELOCITY: (0.001*i, 0.0001*i, 0.0001*i),
                             CUBA.MATERIAL_TYPE: material_uid})
            uids = foo.add_particles([p])
            particles_uids.extend(uids)

        # add to wrapper
        self.wrapper.add_dataset(foo)
        foo_w = self.wrapper.get_dataset(foo.name)

        # remove one particle and update another
        uid_to_remove = particles_uids[len(particles_uids)/2]
        uid_to_update = particles_uids[len(particles_uids)/2-1]

        foo_w.remove_particles([uid_to_remove])
        foo.remove_particles([uid_to_remove])

        # update another point
        p = foo.get_particle(uid_to_update)
        p.coordinates = (1.42, 1.42, 1.42)
        p.data[CUBA.VELOCITY] = (0.0042, 0.0042, 0.0042)
        foo.update_particles([p])
        foo_w.update_particles([p])

        # check if information matches up
        for p in foo.iter_particles():
            p_w = foo_w.get_particle(p.uid)
            assert_almost_equal(p_w.coordinates, p.coordinates)
            assert_almost_equal(p_w.data[CUBA.VELOCITY], p.data[CUBA.VELOCITY])

        # run lammps-engine for 0 steps
        self.wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = 0
        self.wrapper.run()

        # check if information matches up
        for p in foo.iter_particles():
            p_w = foo_w.get_particle(p.uid)

            assert_almost_equal(p_w.coordinates, p.coordinates)
            assert_almost_equal(p_w.data[CUBA.VELOCITY], p.data[CUBA.VELOCITY])

        # update again
        p = foo.get_particle(uid_to_update)
        p.coordinates = (1.24, 1.24, 1.24)
        foo.update_particles([p])
        foo_w.update_particles([p])

        self.wrapper.run()
        # check if information matches up
        for p in foo.iter_particles():
            p_w = foo_w.get_particle(p.uid)
            assert_almost_equal(p_w.coordinates, p.coordinates)

        self.wrapper.run()
        for p in foo.iter_particles():
            p_w = foo_w.get_particle(p.uid)
            assert_almost_equal(p_w.coordinates, p.coordinates)

    def test_run_incomplete_cm(self):
        self._md_configurator.configure_wrapper(self.wrapper)

        # remove CM configuration
        self.wrapper.CM.clear()

        with self.assertRaises(RuntimeError):
            self.wrapper.run()
