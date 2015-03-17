import unittest

from simphony.core.cuba import CUBA
from simphony.cuds.particles import Particles, Particle
from simlammps.cuba_extension import CUBAExtension
from simlammps.lammps_wrapper import LammpsWrapper
from simlammps.tests.example_configurator import ExampleConfigurator


def _create_pc(name):
    """ create particle container with a few particles """
    pc = Particles(name)

    pc.add_particle(Particle(coordinates=(1.01, 1.01, 1.01)))
    pc.add_particle(Particle(coordinates=(1.02, 1.02, 1.02)))

    return pc


class TestLammpsParticles(unittest.TestCase):

    def setUp(self):

        self.wrapper = LammpsWrapper()

    def test_add_particles(self):
        self.wrapper.add_particles(_create_pc("foo"))
        self.wrapper.get_particles("foo")

    def test_add_same_particles(self):
        self.wrapper.add_particles(_create_pc("foo"))
        with self.assertRaises(ValueError):
            self.wrapper.add_particles(_create_pc("foo"))

    def test_get_non_existing_particles(self):
        with self.assertRaises(KeyError):
            self.wrapper.get_particles("foo")

    def test_delete_particles(self):
        self.wrapper.add_particles(_create_pc("foo"))
        self.wrapper.get_particles("foo")

        self.wrapper.delete_particles("foo")

        with self.assertRaises(KeyError):
            self.wrapper.get_particles("foo")

    def test_delete_non_existing_particles(self):
        with self.assertRaises(KeyError):
            self.wrapper.delete_particles("foo")

    def test_particles_rename(self):
        pc = self.wrapper.add_particles(_create_pc("foo"))
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
        self.wrapper.add_particles(Particles(name="foo"))

    def test_iter_particles(self):
        self.wrapper.add_particles(_create_pc("foo"))
        self.wrapper.add_particles(_create_pc("bar"))

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
        ExampleConfigurator.configure_wrapper(self.wrapper)
        self.wrapper.run()

    def test_0_step_run(self):
        ExampleConfigurator.set_configuration(self.wrapper)

        # set pair potentials for one type
        potentials = ("lj:\n"
                      "  global_cutoff: 1.12246\n"
                      "  parameters:\n"
                      "  - pair: [1, 1]\n"
                      "    epsilon: 1.0\n"
                      "    sigma: 1.0\n"
                      "    cutoff: 1.2246\n")
        self.wrapper.SP_extension[CUBAExtension.PAIR_POTENTIALS] = potentials

        # create a pc with 10 particles
        foo = Particles(name="foo")
        data = foo.data
        data[CUBA.MATERIAL_TYPE] = 1
        data[CUBA.MASS] = 1
        foo.data = data

        for i in range(0, 10):
            p = Particle(coordinates=(1+0.1*i, 1+0.1*i, 1+0.1*i))
            p.data[CUBA.VELOCITY] = (1+0.1*i, 1+0.1*i, 1+0.1*i)
            foo.add_particle(p)

        # add to wrapper
        foo_wrapper = self.wrapper.add_particles(foo)

        # add box vectors to data_extension
        box_vectors = [(2.0, 0.0, 0.0),
                       (0.0, 2.0, 0.0),
                       (0.0, 0.0, 2.0)]
        foo_wrapper.data_extension[CUBAExtension.BOX_VECTORS] = box_vectors

        # check if information matches up
        for p in foo.iter_particles():
            p_w = foo_wrapper.get_particle(p.uid)
            self.assertEqual(p_w.coordinates, p.coordinates)
            self.assertEqual(p_w.data[CUBA.VELOCITY], p.data[CUBA.VELOCITY])

        # run lammps-engine for 0 steps
        self.wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = 0
        self.wrapper.run()

        # check if information matches up
        for p in foo.iter_particles():
            p_w = foo_wrapper.get_particle(p.uid)
            self.assertEqual(p_w.coordinates, p.coordinates)
            self.assertEqual(p_w.data[CUBA.VELOCITY], p.data[CUBA.VELOCITY])

    def test_run_incomplete_CM(self):
        ExampleConfigurator.configure_wrapper(self.wrapper)

        # remove CM configuration
        self.wrapper.CM.clear()

        with self.assertRaises(RuntimeError):
            self.wrapper.run()


if __name__ == '__main__':
    unittest.main()
