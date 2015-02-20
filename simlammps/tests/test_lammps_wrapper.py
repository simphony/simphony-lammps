import unittest
from sets import Set

from simphony.cuds.particles import ParticleContainer, Particle
from simlammps.lammps_wrapper import LammpsWrapper
from simlammps.tests.example_configurator import ExampleConfigurator


def _create_pc(name):
    """ create particle container with a few particles """
    pc = ParticleContainer(name)

    pc.add_particle(Particle(coordinates=(1.01, 1.01, 1.01)))
    pc.add_particle(Particle(coordinates=(1.02, 1.02, 1.02)))

    return pc


class TestLammpsParticleContainer(unittest.TestCase):

    def setUp(self):

        self.wrapper = LammpsWrapper()

    def test_add_particle_container(self):
        self.wrapper.add_particle_container(_create_pc("foo"))
        self.wrapper.get_particle_container("foo")

    def test_add_same_particle_container_twice(self):
        self.wrapper.add_particle_container(_create_pc("foo"))
        with self.assertRaises(ValueError):
            self.wrapper.add_particle_container(_create_pc("foo"))

    def test_get_non_existing_particle_container(self):
        with self.assertRaises(KeyError):
            self.wrapper.get_particle_container("foo")

    def test_delete_particle_container(self):
        self.wrapper.add_particle_container(_create_pc("foo"))
        self.wrapper.get_particle_container("foo")

        self.wrapper.delete_particle_container("foo")

        with self.assertRaises(KeyError):
            self.wrapper.get_particle_container("foo")

    def test_delete_non_existing_particle_container(self):
        with self.assertRaises(KeyError):
            self.wrapper.delete_particle_container("foo")

    def test_particle_container_rename(self):
        pc = self.wrapper.add_particle_container(_create_pc("foo"))
        pc.name = "bar"

        # we should not be able to use the old name "foo"
        with self.assertRaises(KeyError):
            self.wrapper.get_particle_container("foo")
        with self.assertRaises(KeyError):
            self.wrapper.delete_particle_container("foo")
        with self.assertRaises(KeyError):
            [_ for _ in self.wrapper.iter_particle_containers(names=["foo"])]

        # we should be able to access using the new "bar" name
        pc_bar = self.wrapper.get_particle_container("bar")
        self.assertEqual("bar", pc_bar.name)

        # and we should be able to use the no-longer used
        # "foo" name when adding another particle container
        pc = self.wrapper.add_particle_container(
            ParticleContainer(name="foo"))

    def test_iter_particle_container(self):
        self.wrapper.add_particle_container(_create_pc("foo"))
        self.wrapper.add_particle_container(_create_pc("bar"))

        pc_name_list = list(
            pc.name for pc in self.wrapper.iter_particle_containers())
        self.assertEqual(len(pc_name_list), 2)

        ordered_names = ["bar", "foo", "bar"]

        self.assertEqual(Set(ordered_names), Set(pc_name_list))

        pc_name_list = list(
            pc.name for pc in self.wrapper.iter_particle_containers(
                ordered_names))
        self.assertEqual(ordered_names, pc_name_list)

    def test_run(self):
        ExampleConfigurator.configure_wrapper(self.wrapper)
        self.wrapper.run()

    def test_run_incomplete_CM(self):
        ExampleConfigurator.configure_wrapper(self.wrapper)

        # remove CM configuration
        self.wrapper.CM.clear()

        with self.assertRaises(RuntimeError):
            self.wrapper.run()


if __name__ == '__main__':
    unittest.main()
