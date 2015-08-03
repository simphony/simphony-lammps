import abc
from functools import partial

from numpy.testing import assert_almost_equal

from simphony.testing.utils import (
    compare_data_containers, compare_particles)
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA
from simphony.cuds.particles import Particles, Particle

from simlammps.testing.md_example_configurator import MDExampleConfigurator


def _create_pc(name):
    """ create particle container with a few particles """
    pc = Particles(name)

    data = DataContainer()

    # TODO these values should be gotten from MDExampleConfigurator
    data[CUBA.MASS] = 1
    data[CUBA.MATERIAL_TYPE] = 1
    pc.data = data

    data = DataContainer()
    data[CUBA.VELOCITY] = (0.0, 0.0, 0.0)

    pc.add_particle(Particle(coordinates=(1.01, 1.01, 1.01), data=data))
    pc.add_particle(Particle(coordinates=(1.02, 1.02, 1.02), data=data))

    return pc


def _get_particle(wrapper):
    """
    get particle and particle container

    """
    for particles in wrapper.iter_particles():
        for p in particles.iter_particles():
            return p, particles
    else:
        raise RuntimeError("could not find a particle to test with")


class ABCLammpsMDEngineCheck(object):

    __metaclass__ = abc.ABCMeta

    def setUp(self):
        self.addTypeEqualityFunc(
            DataContainer, partial(compare_data_containers, testcase=self))
        self.addTypeEqualityFunc(
            Particle, partial(compare_particles, testcase=self))
        self.wrapper = self.engine_factory()

    @abc.abstractmethod
    def engine_factory(self):
        """ Create and return the engine
        """

    def test_add_particles(self):
        MDExampleConfigurator.add_configure_particles(self.wrapper,
                                                      _create_pc("foo"))
        self.wrapper.get_particles("foo")

    def test_add_same_particles(self):
        MDExampleConfigurator.add_configure_particles(self.wrapper,
                                                      _create_pc("foo"))
        with self.assertRaises(ValueError):
            self.wrapper.add_particles(_create_pc("foo"))

    def test_get_non_existing_particles(self):
        with self.assertRaises(KeyError):
            self.wrapper.get_particles("foo")

    def test_delete_particles(self):
        MDExampleConfigurator.add_configure_particles(self.wrapper,
                                                      _create_pc("foo"))
        self.wrapper.get_particles("foo")

        self.wrapper.delete_particles("foo")

        with self.assertRaises(KeyError):
            self.wrapper.get_particles("foo")

    def test_delete_non_existing_particles(self):
        with self.assertRaises(KeyError):
            self.wrapper.delete_particles("foo")

    def test_particles_rename(self):
        pc = MDExampleConfigurator.add_configure_particles(self.wrapper,
                                                           _create_pc("foo"))
        pc.name = "bar"

        # we should not be able to use the old name "foo"
        with self.assertRaises(KeyError):
            self.wrapper.get_particles("foo")
        with self.assertRaises(KeyError):
            self.wrapper.delete_particles("foo")
        with self.assertRaises(KeyError):
            [_ for _ in self.wrapper.iter_particles(names=["foo"])]

        # we should be able to access using the new "bar" name
        pc_bar = self.wrapper.get_particles("bar")
        self.assertEqual("bar", pc_bar.name)

        # and we should be able to use the no-longer used
        # "foo" name when adding another container of particles
        self.wrapper.add_particles(_create_pc("foo"))

    def test_iter_particles(self):
        MDExampleConfigurator.add_configure_particles(self.wrapper,
                                                      _create_pc("foo"))
        MDExampleConfigurator.add_configure_particles(self.wrapper,
                                                      _create_pc("bar"))

        pc_name_list = list(
            pc.name for pc in self.wrapper.iter_particles())
        self.assertEqual(len(pc_name_list), 2)

        ordered_names = ["bar", "foo", "bar"]

        self.assertEqual(set(ordered_names), set(pc_name_list))

        pc_name_list = list(
            pc.name for pc in self.wrapper.iter_particles(
                ordered_names))
        self.assertEqual(ordered_names, pc_name_list)

    def test_run(self):
        MDExampleConfigurator.configure_wrapper(self.wrapper)
        self.wrapper.run()

    # TODO not yet supported
    def DUMMY_test_run_delete_particle(self):
        MDExampleConfigurator.configure_wrapper(self.wrapper)

        removed_particle, particles = _get_particle(self.wrapper)
        particles.remove_particle(removed_particle.uid)

        # check that it was removed
        with self.assertRaises(KeyError):
            particles.get_particle(removed_particle.uid)

        self.wrapper.run()

        # check that it stayed removed
        with self.assertRaises(KeyError):
            particles.get_particle(removed_particle.uid)

    def test_0_step_run(self):
        MDExampleConfigurator.configure_wrapper(self.wrapper)

        foo = Particles(name="foo")
        for i in range(0, 10):
            p = Particle(coordinates=(1+0.1*i, 1+0.1*i, 0+0.1*i))
            p.data[CUBA.VELOCITY] = (1+0.1*i, 1+0.1*i, 1+0.1*i)
            foo.add_particle(p)

        # add to wrapper
        foo_w = MDExampleConfigurator.add_configure_particles(self.wrapper,
                                                              foo)

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

    def test_run_incomplete_cm(self):
        MDExampleConfigurator.configure_wrapper(self.wrapper)

        # remove CM configuration
        self.wrapper.CM.clear()

        with self.assertRaises(RuntimeError):
            self.wrapper.run()
