import unittest
from sets import Set

from simphony.cuds.particles import ParticleContainer, Particle
from simlammps.lammps_wrapper import LammpsWrapper
from simlammps.dummy import LammpsDummyConfig


def _create_pc():
    """ create particle container with a few particles """
    pc = ParticleContainer()

    pc.add_particle(Particle(coordinates=(1.01, 1.01, 1.01)))
    pc.add_particle(Particle(coordinates=(1.02, 1.02, 1.02)))

    return pc


class TestLammpsParticleContainer(unittest.TestCase):

    def setUp(self):

        self.wrapper = LammpsWrapper()

    def test_add_particle_container(self):
        self.wrapper.add_particle_container("foo")
        self.wrapper.get_particle_container("foo")

        self.wrapper.add_particle_container("bar", _create_pc())
        self.wrapper.get_particle_container("bar")

    def test_add_same_particle_container_twice(self):
        self.wrapper.add_particle_container("foo")
        with self.assertRaises(Exception):
            self.wrapper.add_particle_container("foo")

    def test_get_non_existing_particle_container(self):
        with self.assertRaises(Exception):
            self.wrapper.get_particle_container("foo")

    def test_delete_particle_container(self):
        self.wrapper.add_particle_container("foo", _create_pc())
        self.wrapper.get_particle_container("foo")

        self.wrapper.delete_particle_container("foo")

        with self.assertRaises(Exception):
            self.wrapper.get_particle_container("foo")

    def test_delete_non_existing_particle_container(self):
        with self.assertRaises(Exception):
            self.wrapper.delete_particle_container("foo")

    def test_iter_particle_container(self):
        self.wrapper.add_particle_container("foo")
        self.wrapper.add_particle_container("bar")

        pc_name_list = list(
            name for name, _pc in self.wrapper.iter_particle_containers())
        self.assertEqual(len(pc_name_list), 2)

        ordered_names = ["bar", "foo", "bar"]

        self.assertEqual(Set(ordered_names), Set(pc_name_list))

        pc_name_list = list(
            name for name, _pc in self.wrapper.iter_particle_containers(
                ordered_names))
        self.assertEqual(ordered_names, pc_name_list)

    def test_run_incomplete_CM(self):
        LammpsDummyConfig.configure_wrapper(self.wrapper)

        # remove CM configuration
        self.wrapper.CM.clear()

        with self.assertRaises(Exception):
            self.wrapper.run()


if __name__ == '__main__':
    unittest.main()
